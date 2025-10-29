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

### 1️⃣ Clone the repository
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