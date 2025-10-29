# 📊 ComparIA – LLM Benchmark Dashboard

**ComparIA** is an interactive **Streamlit dashboard** designed to benchmark and visualize the performance of multiple **Large Language Models (LLMs)** across diverse categories of tasks.  
It combines **quality**, **latency**, **energy consumption**, and **CO₂ emissions** to analyze trade-offs between **performance and efficiency**.

---

## 🧠 Overview

This project allows you to:

- 📈 **Compare** LLMs by size and task category  
- ⚙️ **Explore** relationships between metrics (Quality vs Energy, Quality vs CO₂, Latency per model size)  
- 🏁 **Rank** models per use case using **custom weights** (Quality, Latency, Energy)  
- 🔍 **Filter** data dynamically by model size, model name, and task type  

All charts are **interactive** and generated with **Plotly**.

---

## 🧱 Project Structure

LLM_BENCHMARCK_DASHBOARD/
│
├── .streamlit/
│ └── config.toml # Optional Streamlit theme configuration
│
├── app/
│ └── data/
│ └── data.csv # Main dataset (LLM benchmark results)
│
├── pages/
│ ├── App.py # Aggregated view (Quality, Energy, CO₂, Latency)
│ ├── Exploration.py # Metric exploration (line & bar charts)
│ └── Ranking.py # Ranking page (weighted scoring system)
│
├── README.md # Documentation (this file)
├── requirements.txt # Dependencies
└── .gitignore


---

## ⚙️ Installation

1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/LLM_BENCHMARCK_DASHBOARD.git
cd LLM_BENCHMARCK_DASHBOARD

2️⃣ Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate        # Windows

3️⃣ Install dependencies
pip install -r requirements.txt


🚀 Running the app

Launch the dashboard:
streamlit run pages/App.py

📊 Dataset Schema
Column	Description
run_id	Unique identifier for each benchmark run
task_id	Numeric ID of the evaluated task
task_label	Text describing the prompt or task
model	Model name (e.g. GPT-5, Gemma 8B)
model_size	Size category (Small / Medium / Large)
quality	Quality score (1–5)
latency_s	Average response time (seconds)
energy_kwh	Energy consumption per run (Wh)
co2_kg	CO₂ emissions per run (g eq.)


🧩 Key Pages

🧭 App.py – Aggregated Dashboard
Bar charts comparing:
Average Quality, Latency, Energy, and CO₂
By Model Size and Task Category

🔬 Exploration.py – Metrics Exploration
Line and bar charts exploring:
Quality vs Energy
Quality vs CO₂ Emissions
Average Latency per Model Size

🏁 Ranking.py – Model Ranking
Ranks models per task category using weighted scoring:
Adjustable sliders for Quality, Latency, and Energy
Interactive Top 5 bar chart per use case
CSV export of the complete ranking


🧠 How the Weighted Ranking Works
Each model gets a normalized score per metric:
Higher is better for Quality
Lower is better for Latency and Energy
The final score is computed as:   Score=wQ​×Q+wL​×(1−L)+wE​×(1−E),

where ( w_Q ), ( w_L ), and ( w_E ) are user-defined weights (whose total does not exceed 1), and all metrics are normalized between 0 and 1 prior to aggregation.

📦 Dependencies
Library	Purpose
streamlit	Web app interface
pandas	Data processing
plotly	Interactive visualizations
numpy	Numerical normalization
pathlib	File system utilities

🧑‍💻 Author

Marie-Pierre DIQUERO & Fares DOSSOGBETE 
MSc Data Engineering & Cloud Computing @ Aivancity Paris
