import pymongo
import ollama
import numpy as np
from datetime import datetime

# ================= 設定區 =================
# Local MongoDB 連線
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "local_chat_db"
COLLECTION_NAME = "memories"

# Local 模型設定
CHAT_MODEL = "qwen3:8b"           # 對話模型
EMBED_MODEL = "nomic-embed-text"  # Embedding 模型
# =========================================

class FullyLocalMemoryAgent:
    def __init__(self):
        print(f">> [初始化] 連線 Local MongoDB...")
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            # 測試連線
            self.client.admin.command('ping')
            print(">> [成功] MongoDB 連線成功！")
        except Exception as e:
            print(f">> [錯誤] MongoDB 連線失敗，請確認 mongod 是否已啟動: {e}")
            exit(1)

    def get_embedding(self, text):
        """呼叫 Ollama 產生 Embedding"""
        # 注意: nomic-embed-text 產出的向量通常不需要再做正規化(Normalize)，
        # 但為了保險起見，計算 Cosine Similarity 時我們會處理。
        response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        return response['embedding']

    def calculate_cosine_similarity(self, vec_a, vec_b):
        """
        數學小教室：計算餘弦相似度
        Similarity = (A . B) / (||A|| * ||B||)
        """
        vec_a = np.array(vec_a)
        vec_b = np.array(vec_b)
        
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        # 避免除以零
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    def search_memory(self, query_text, limit=3):
        """
        手動實作向量搜尋 (Client-side Vector Search)
        適用於資料量 < 10,000 筆的小型專案
        """
        # 1. 取得當前問題的向量
        query_vector = self.get_embedding(query_text)
        
        # 2. 把所有記憶撈出來 (實務上可以只撈最近 N 筆或加過濾條件)
        # 為了效能，我們只取出需要的欄位
        cursor = self.collection.find({}, {"text": 1, "embedding": 1, "timestamp": 1})
        all_memories = list(cursor)
        
        if not all_memories:
            return []

        # 3. 逐一計算相似度 (這就是 Vector DB 在做的事)
        scored_memories = []
        for doc in all_memories:
            score = self.calculate_cosine_similarity(query_vector, doc['embedding'])
            # 設定一個門檻值，太不相關的不要 (例如 < 0.3)
            if score > 0.4: 
                doc['score'] = score
                scored_memories.append(doc)
        
        # 4. 依照分數高低排序，並取前幾名
        scored_memories.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_memories[:limit]

    def save_memory(self, user_text, ai_text):
        conversation = f"User: {user_text}\nAI: {ai_text}"
        vector = self.get_embedding(conversation)
        
        doc = {
            "text": conversation,
            "embedding": vector,
            "timestamp": datetime.now()
        }
        self.collection.insert_one(doc)

    def chat(self, user_input):
        # 1. 檢索 (Retrieval)
        memories = self.search_memory(user_input)
        
        memory_context = ""
        if memories:
            print(f"\n>> [大腦] 聯想到 {len(memories)} 段回憶：")
            for m in memories:
                print(f"   - (相似度 {m['score']:.2f}) {m['text'][:30]}...") # 只印前30字避免洗版
                memory_context += f"- {m['text']} (時間: {m['timestamp']})\n"
        else:
            print("\n>> [大腦] 沒有相關的過去回憶。")

        # 2. 組裝 Prompt
        system_prompt = f"""
        你是一個使用 Local MongoDB 作為長期記憶的 AI 助手。
        請根據使用者的問題回答。
        
        參考記憶：
        {memory_context}
        
        請用繁體中文回答，並盡量自然。
        """

        # 3. 生成 (Generation)
        print(">> [Qwen] 思考中...", end="", flush=True)
        stream = ollama.chat(
            model=CHAT_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input},
            ],
            stream=True,
        )

        full_response = ""
        print("\rAI: ", end="")
        for chunk in stream:
            content = chunk['message']['content']
            print(content, end="", flush=True)
            full_response += content
        print("\n")

        # 4. 儲存 (Storage)
        self.save_memory(user_input, full_response)

if __name__ == "__main__":
    bot = FullyLocalMemoryAgent()
    print(f"=== 全 Local 端長期記憶對話系統 ===")
    print(f"DB: localhost:27017 | Model: {CHAT_MODEL}")
    
    while True:
        try:
            user_in = input("\n你: ")
            if user_in.lower() in ['exit', 'quit']:
                break
            if not user_in.strip():
                continue
                
            bot.chat(user_in)
        except KeyboardInterrupt:
            break
