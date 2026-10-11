# Impact of Heating Season and Meteorological Conditions on Air Pollution in Almaty

## Project Information
* **Author:** Abildayev Dinmukhdammed
* **Course / Context:** Applied Data Science Research
* **Research Type:** Quantitative Research / Quasi-Experimental Study

## Research Question
How do heating season emissions and meteorological calm (wind speed $< 1.0\text{ m/s}$) synergistically impact fine particulate matter concentrations ($\text{PM}_{2.5}$, $\text{PM}_{10}$) and $\text{NO}_2$ in the mountain basin of Almaty?

## Repository Structure
```text
almaty-air-pollution-analysis/
├── configs/
│   └── config.yaml          # Experiment parameters & variable settings
├── data/
│   └── sample/
│       └── almaty_air_sample.csv # 8-row sample data for pipeline testing
├── src/
│   └── benchmark.py         # Main execution code for benchmarking
├── .gitignore               # Strict git ignore patterns for Python
├── Dockerfile               # Container configuration with pinned exact dependencies
├── LICENSE                  # Open-source MIT License
├── README.md                # Project documentation and quickstart guide
└── requirements.txt         # Exact pinned Python package dependencies
```

## Planned Benchmarks & Metrics

| Metric Category | Metric Name | Definition / Target | Role |
| :--- | :--- | :--- | :--- |
| **Primary** | Mean Difference ($\Delta \bar{X}$) | $\mu_{\text{winter}} - \mu_{\text{summer}}$ ($\text{PM}_{2.5}$) | Assess seasonal shift |
| **Primary** | Interaction Coeff ($\beta_3$) | Synergy coefficient ($p < 0.05$) | Test $H_{1,2}$ synergy |
| **Guardrail** | Missing Data Rate (MDR) | $\le 15\%$ missing entries per sensor | Data integrity safeguard |
| **Guardrail** | Calibration $R^2$ | $R^2_{\text{calib}} \ge 0.75$ with reference stations | Sensor drift control |
| **Pipeline** | Processing Latency | Time to run benchmark pipeline (ms) | Speed & efficiency |

---

## Quickstart Guide

Run the pipeline benchmark in **2 simple steps**:

### Option 1: Local Python Environment
```bash
# 1. Install pinned dependencies
pip install -r requirements.txt

# 2. Run the benchmark script on the sample dataset
python src/benchmark.py
```

### Option 2: Docker Environment
```bash
# 1. Build Docker image
docker build -t almaty-air-benchmark .

# 2. Run benchmark inside container
docker run --rm almaty-air-benchmark
```

# 2. Run benchmark inside container
docker run --rm almaty-air-benchmark
## License
Distributed under the MIT License.


