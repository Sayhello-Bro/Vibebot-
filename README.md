# BCAT — Bounded Confidence and Adoption Threshold Model

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19216365.svg)](https://doi.org/10.5281/zenodo.19216365)
[![protocols.io](https://img.shields.io/badge/protocols.io-DOI-green)](https://www.protocols.io/view/reproducing-simulation-results-for-the-bcat-model-jwrwcpd7f)
[![CANS Lab](https://img.shields.io/badge/CANS_Lab-Homepage-orange)](https://canslab1.github.io/)

A mixed opinion dynamics and innovation diffusion simulation model for exploring the "best game no one played" phenomenon.

## Companion Manuscript Repository

The manuscript source files, figures, and supporting information for the accompanying PLOS ONE paper are hosted separately:

- **Manuscript Repository:** [github.com/canslab1/PLOS-BCAT](https://github.com/canslab1/PLOS-BCAT)

## Overview

The BCAT (Bounded Confidence + Adoption Threshold) model integrates a bounded confidence-based opinion dynamics model with an adoption threshold innovation diffusion model. It simulates opinion exchanges and product acceptance behaviors across four types of theoretical social networks:

- **Regular Lattice (CA)**: Toroidal 2D cellular automata with Moore neighborhood (rewiring probability = 0)
- **Small-World Network (SWN)**: Watts-Strogatz model (0 < rewiring probability < 1)
- **Random Network (RN)**: Fully rewired network (rewiring probability = 1)
- **Scale-Free Network (SFN)**: Barabasi-Albert preferential attachment model

Each simulation consists of 400 agents connected by approximately 1,600 edges, with an average of 8 neighbors per agent.

## Features

- **Mixed model** — Integrates bounded confidence opinion dynamics with adoption threshold innovation diffusion in a single simulation.
- **Four network topologies** — Regular Lattice (CA), Small-World (SWN), Random (RN), and Scale-Free (SFN) networks.
- **Interactive GUI** — Tkinter-based interface with real-time visualization of attitude trajectories, social networks, adoption dynamics, and distributions.
- **Batch experiments** — Run multiple repetitions with automatic result aggregation.
- **Reproducible scenarios** — Pre-configured parameter files for reproducing all key paper figures.
- **Dual implementation** — Both Python 3 (with GUI) and NetLogo 4.0.5 versions producing statistically equivalent results.

## Installation

### Python Version

- Python 3.10 or later (tested on Python 3.12 and 3.13)

### Setup

```bash
git clone https://github.com/canslab1/BCAT.git
cd BCAT
pip install -r requirements.txt
```

### Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install numpy>=1.24.0 networkx>=3.0 matplotlib>=3.7.0
```

### Standard Library Modules (no installation needed)

`tkinter`, `random`, `os`, `time`, `math`, `threading`, `pickle`, `warnings`

### NetLogo Version (for `.nlogo` file)

- NetLogo 4.0.5 or later (available at https://ccl.northwestern.edu/netlogo/)

## Usage

### Python Version

```bash
python3 BCAT.py
```

This launches the GUI application with:
- **Left panel**: Parameter sliders, control buttons, Social Network visualization, and monitors
  - Social Network with legend (red = adopter; green gradient = non-adopter attitude level)
  - Monitors: Critical (critical point tick), FRI (Favorable Review Index), GSI (Good Sales Index)
- **Right panel**: Real-time visualization plots (4 rows, all titles in blue bold)
  - Row 1: Attitude Distribution, Threshold Distribution, Degree Distribution
  - Row 2: Attitude Trajectory with density colorbar legend (full-width, grid lines)
  - Row 3: Adoption Dynamics (adopter vs. non-adopter counts, full-width, grid lines)
  - Row 4: New Adopter Dynamics (full-width, grid lines)

### Controls

| Button | Function |
|--------|----------|
| **Setup** | Initialize the network and agent population |
| **Run** | Execute a complete simulation run (max-time steps) |
| **Run Once** | Execute a single time step |
| **Experiments** | Run batch experiments (no-of-experiments repetitions) |
| **Save** | Save current model state |
| **Load** | Load a previously saved model state |

### NetLogo Version

1. Open `English - best game no one played.nlogo` in NetLogo 4.0.5+
2. Adjust parameters using the interface sliders
3. Click "Setup" to initialize, then "Run once" to execute

## Model Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `no-of-pioneers` | 0 -- 100 | 5 | Number of initial adopter agents |
| `clustered-pioneers?` | ON/OFF | ON | Whether pioneers are spatially clustered |
| `bounded-confidence` | 0 -- 90 | 50 | Attitude distance threshold for opinion exchange |
| `convergence-rate` | 0.1 -- 1.0 | 0.1 | Rate of attitude adjustment per exchange |
| `avg-of-attitudes` | 10 -- 100 | 50 | Mean of initial attitude distribution |
| `std-of-attitudes` | 0 -- 30 | 10 | Std. dev. of initial attitude distribution |
| `avg-of-thresholds` | 10 -- 100 | 40 | Mean of adoption threshold distribution |
| `std-of-thresholds` | 0 -- 30 | 10 | Std. dev. of adoption threshold distribution |
| `network-type` | SFN / SWN | SWN/RN/CA | Social network topology |
| `rewiring-probability` | 0.00 -- 1.00 | 0.00 | Network rewiring probability (SWN only) |
| `max-time` | 50 -- 1000 | 300 | Maximum simulation time steps |
| `no-of-experiments` | 10 -- 1000 | 20 | Number of batch experiment repetitions |

## Reproducing Paper Results

Parameter configuration files for reproducing the simulation scenarios presented in the paper are provided in the `test_scenarios/` directory.

### Scenario 1: Favorable Review + Good Sales (Fig. 4)

```
python3 BCAT.py
```
Then set parameters: no-of-pioneers=5, clustered-pioneers=ON, bounded-confidence=50, convergence-rate=0.1, avg-of-attitudes=50, std-of-attitudes=10, avg-of-thresholds=20, std-of-thresholds=5, network-type=SWN/RN/CA, rewiring-probability=0.00, max-time=300. Click Setup, then Run.

### Scenario 2: Downward Compatibility -- Opinion Dynamics Only (Fig. 11)

Set: avg-of-thresholds=100, std-of-thresholds=0, no-of-pioneers=0, bounded-confidence=10, convergence-rate=0.4, avg-of-attitudes=50, std-of-attitudes=20, network-type=SWN/RN/CA, rewiring-probability=0.00, max-time=300.

### Scenario 3: Downward Compatibility -- Adoption Threshold Only (Fig. 12)

Set: avg-of-attitudes=100, std-of-attitudes=0, bounded-confidence=0, avg-of-thresholds=20, std-of-thresholds=10, no-of-pioneers=3, network-type=SWN/RN/CA, rewiring-probability=0.00, max-time=50.

## Model Algorithm

The BCAT model operates in the following phases per time step:

1. **Agent Selection**: All agents are processed in random order each tick.
2. **Neighbor Selection**: Each agent randomly selects one neighboring agent.
3. **Opinion Exchange**: If the attitude difference is below the bounded confidence threshold, attitudes are adjusted according to four scenarios based on adoption status (see Algorithm 3 in the paper).
4. **Adoption Decision**: A not-yet-adopted agent with a positive attitude (att > 50) adopts if the proportion of adopted neighbors exceeds its adoption threshold.

## Implementation Notes

- The Python version faithfully replicates the NetLogo 4.0.5 implementation, including the sequential execution semantics of NetLogo's `ask-concurrent` (which processes agents in random order with immediate effect).
- `int(v + 0.5)` is used as an equivalent to NetLogo's `round()` for positive values.
- NumPy arrays replace NetLogo's `turtles-own` for performance optimization.
- NetworkX graphs replace NetLogo's native turtle/link network structure.
- Both versions produce statistically equivalent results under identical random seeds and parameter settings.
- **Attitude Trajectory rendering optimization**: scatter points are grouped by color into 15 fixed PathCollection objects and updated incrementally via `set_offsets()`, reducing `draw_idle()` artist traversal from O(T×K) to O(1).
- **Dual-Figure architecture**: Social Network is rendered on a separate matplotlib Figure embedded in the left panel, allowing the three time-series plots (Attitude Trajectory, Adoption Dynamics, New Adopter Dynamics) to share a full-width X axis (Time) in the right panel.
- **Evaluation metrics**: FRI (Favorable Review Index = agents with attitude > 50 / total agents) and GSI (Good Sales Index = adopters / total agents) update in real time, displayed to 4 decimal places.
- **Chart legends**: Attitude Trajectory includes a 15-color density colorbar; Social Network legend shows node color meanings (adopter, attitude levels) without overlapping the graph.
- **Degree Distribution alignment**: bars are centered on integer ticks using `ax.bar()` instead of `ax.hist()` for accurate visual correspondence.

## Data

The `data/` directory contains the simulation output data underlying the tables and figures in the accompanying paper. These files constitute the minimal dataset required for replication.

### Sensitivity Analysis (`data/sensitivity_analysis/`)

Raw output from 1,000-run batch experiments across four network topologies, used to generate Table 3 and Figs 7–9 in the paper.

| File | Network Topology | Format |
|------|-----------------|--------|
| `sensitivity_analysis_regular_lattice.xlsx` | Regular Lattice (CA) | Excel |
| `sensitivity_analysis_small_world.xlsx` | Small-World (SWN) | Excel |
| `sensitivity_analysis_random.xlsx` | Random (RN) | Excel |
| `sensitivity_analysis_scale_free.xlsx` | Scale-Free (SFN) | Excel |

Each workbook contains per-run records of adoption outcomes (adopter counts, critical points) across systematic parameter sweeps of the five primary model parameters.

### Mechanism Decomposition (`data/mechanism_decomposition/`)

Results from three controlled experiments designed to disentangle the opinion clustering channel and the coordination failure channel in the opinion–adoption gap (Fig 10 in the paper, 30,000 total simulation runs).

| File | Experiment | Topology | Runs | Description |
|------|-----------|----------|------|-------------|
| `md_a_lattice.csv` | MD-A | Regular Lattice | 7,000 | Coordination failure isolated (FRI = 1.0 by construction) |
| `md_a_smallworld.csv` | MD-A | Small-World | 7,000 | Coordination failure isolated (FRI = 1.0 by construction) |
| `md_b_lattice.csv` | MD-B | Regular Lattice | 1,000 | Opinion clustering isolated (no pioneers, GSI = 0) |
| `md_b_smallworld.csv` | MD-B | Small-World | 1,000 | Opinion clustering isolated (no pioneers, GSI = 0) |
| `md_c_lattice.csv` | MD-C | Regular Lattice | 7,000 | Full BCAT baseline (both channels active) |
| `md_c_smallworld.csv` | MD-C | Small-World | 7,000 | Full BCAT baseline (both channels active) |

**CSV columns**: `experiment` (run index), `fri` (Favorable Review Index at t=300), `gsi` (Good Sales Index at t=300), `adopters` (final adopter count), `N` (population size), `avg_of_thresholds` (threshold parameter), `experiment_id` (MD-A/MD-B/MD-C), `topology` (lattice/smallworld).

### Finite-Size Scaling (`data/finite_size_scaling/`)

Results from scaling experiments at N=400, 900, 1,600, and 2,500 agents, confirming that the "best game no one played" phenomenon and the dominance of avg-of-thresholds are robust to system size.

| File | Description |
|------|-------------|
| `finite_size_scaling_results.csv` | Raw per-run results across all system sizes |
| `summary_by_threshold_and_N.csv` | Aggregated mean FRI/GSI by threshold and N |

## Scripts

The `scripts/` directory contains Python scripts for reproducing the paper's analyses and figures:

| Script | Purpose |
|--------|---------|
| `reproduce_table3_figs.py` | Reproduce Table 3 and Figs 7–9 from sensitivity analysis data |
| `generate_table3_and_figs.py` | Generate Table 3 values and figure images |
| `run_mechanism_decomposition.py` | Run MD-A/B/C mechanism decomposition experiments |
| `finite_size_scaling.py` | Run finite-size scaling experiments at N=900, 1,600, 2,500 |

## Project Structure

```
BCAT/
├── BCAT.py                                # Python 3 implementation with GUI (Tkinter + matplotlib)
├── English - best game no one played.nlogo # NetLogo 4.0.5 implementation
├── requirements.txt                       # Python dependencies
├── pyproject.toml                         # Project metadata (PEP 621)
├── CITATION.cff                           # Citation metadata
├── CHANGELOG.md                           # Version history
├── CONTRIBUTING.md                        # Contribution guidelines
├── COMPLEXITY_ANALYSIS.md                 # Time/space complexity analysis
├── data/                                  # Simulation output data for paper replication
│   ├── sensitivity_analysis/              # 1,000-run batch results (4 network topologies)
│   ├── mechanism_decomposition/           # MD-A/B/C experiments (30,000 runs, CSV)
│   └── finite_size_scaling/               # Scaling experiments (N=400–2,500)
├── scripts/                               # Analysis and experiment scripts
│   ├── reproduce_table3_figs.py           # Reproduce Table 3 and Figs 7–9
│   ├── generate_table3_and_figs.py        # Generate Table 3 values and figures
│   ├── run_mechanism_decomposition.py     # Run MD-A/B/C experiments
│   └── finite_size_scaling.py             # Run finite-size scaling experiments
├── test_scenarios/                        # Parameter configs for paper reproduction
│   ├── fig4_favorable_review_good_sales.json
│   ├── fig5_favorable_review_poor_sales.json
│   ├── fig11_opinion_dynamics_only.json
│   ├── fig12_adoption_threshold_only.json
│   └── sensitivity_analysis_1000_runs.json
├── LICENSE                                # MIT License
├── index.html                             # GitHub Pages landing page
├── 404.html                               # Custom 404 error page
├── sitemap.xml                            # XML sitemap for search engines
├── robots.txt                             # Crawler directives
└── llms.txt                               # AI-readable project summary
```

## Authors

- **Chung-Yuan Huang** (黃崇源) — Department of Computer Science and Information Engineering, Chang Gung University, Taiwan (gscott@mail.cgu.edu.tw)
- **Sheng-Wen Wang** (Corresponding author) — Department of Finance and Information, National Kaohsiung University of Science and Technology, Taiwan (swwang@nkust.edu.tw)

## Citation

See `CITATION.cff` for machine-readable citation metadata.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
