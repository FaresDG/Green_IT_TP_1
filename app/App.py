import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# ---- CONFIG ----
st.set_page_config(
    page_title="ComparIA – LLM Benchmark Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---- STYLE ----
st.markdown("""
    <style>
    h1, h2, h3 {font-weight: 600; color: #E5E7EB;}
    .stMetric label {color: #A5B4FC; font-weight: 500;}
    .stMetric div[data-testid="stMetricValue"] {
        color: #F9FAFB; font-size: 2rem; font-weight: 700;
    }
    .stDataFrame {border-radius: 12px !important;}
    .stDataFrame table {border: 1px solid #374151 !important;}
    </style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("📊 ComparIA — LLM Benchmark Dashboard")

st.divider()

# ---- DATA LOADING ----
DATA_PATH = Path(__file__).parent / "data" / "data.csv"

@st.cache_data
def load_data():
    if DATA_PATH.exists():
        try:
            df = pd.read_csv(
                DATA_PATH,
                sep=";",
                quotechar='"',
                engine="python",
                encoding="latin-1"
            )

            # Numeric columns conversion
            num_cols = ["quality", "latency_s", "energy_wh", "co2_g"]
            for col in num_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Expected columns check
            expected_cols = [
                "run_id", "task_id", "task_label", "model",
                "model_size", "quality", "latency_s",
                "energy_wh", "co2_g"
            ]
            missing = [c for c in expected_cols if c not in df.columns]
            if missing:
                st.error(f" Missing columns in CSV: {missing}")
            else:
                st.success(" Data loaded successfully.")

            return df

        except Exception as e:
            st.error(f"Error while reading CSV: {e}")
            return pd.DataFrame()
    else:
        st.warning(" No data.csv file found in app/data/.")
        return pd.DataFrame()

df = load_data()

# ---- TASK CATEGORY ----
def categorize_task(task_id):
    if 1 <= task_id <= 10:
        return "Easy factual & rewriting"
    elif 11 <= task_id <= 15:
        return "Reasoning & quantitative"
    elif 16 <= task_id <= 20:
        return "Programming & debugging"
    elif 21 <= task_id <= 25:
        return "Harder knowledge & reasoning"
    elif 26 <= task_id <= 30:
        return "Advanced / creative & multi-step"
    else:
        return "Other"

if not df.empty and "task_id" in df.columns:
    df["task_category"] = df["task_id"].apply(categorize_task)

# ---- SIDEBAR ----
st.sidebar.header("⚙️ Filters")

if df.empty:
    df_filtered = df
else:
    # 1️⃣ Model sizes
    sizes_all = sorted(df["model_size"].dropna().unique())
    size_sel = st.sidebar.multiselect("Model sizes", sizes_all, default=sizes_all)

    if len(size_sel) == 0:
        st.sidebar.warning("Select at least one model size.")
        df_filtered = df.iloc[0:0]  # empty
    else:
        df_size = df[df["model_size"].isin(size_sel)]

        # 2️⃣ Task categories (linked to size)
        cats_all = sorted(df_size["task_category"].dropna().unique()) if "task_category" in df_size.columns else []
        cat_sel = st.sidebar.multiselect("Task categories", cats_all, default=cats_all)

        df_size_cat = df_size[df_size["task_category"].isin(cat_sel)] if len(cat_sel) else df_size.iloc[0:0]

        # 3️⃣ Models (linked to size + category)
        models_all = sorted(df_size_cat["model"].dropna().unique())
        model_sel = st.sidebar.multiselect("Models", models_all, default=models_all)

        # 🔹 Final filtering
        df_filtered = df[
            df["model_size"].isin(size_sel)
            & df["task_category"].isin(cat_sel)
            & df["model"].isin(model_sel)
        ]

# ---- AGGREGATION ----
if not df_filtered.empty:
    agg = (
        df_filtered.groupby(["task_category", "model_size"], as_index=False)
        .agg({
            "quality": "mean",
            "latency_s": "mean",
            "energy_wh": "mean",
            "co2_g": "mean"
        })
        .round(3)
    )

    st.subheader("📊 Averages Table")
    st.dataframe(agg, use_container_width=True)

    # ---- VISUALIZATIONS ----
    st.subheader("📈Quality, energy, CO₂, and latency by model size and task category. ")
    tabs = st.tabs(["Quality", "Latency", "Energy", "CO₂"])

    with tabs[0]:
        fig_q = px.bar(agg, x="task_category", y="quality", color="model_size",
                       barmode="group", title="Average Quality by Task Category and Model Size")
        st.plotly_chart(fig_q, use_container_width=True)

    with tabs[1]:
        fig_l = px.bar(agg, x="task_category", y="latency_s", color="model_size",
                       barmode="group", title="Average Latency (s)")
        st.plotly_chart(fig_l, use_container_width=True)

    with tabs[2]:
        fig_e = px.bar(agg, x="task_category", y="energy_wh", color="model_size",
                       barmode="group", title="Average Energy Consumption (wh)")
        st.plotly_chart(fig_e, use_container_width=True)

    with tabs[3]:
        fig_co2 = px.bar(agg, x="task_category", y="co2_g", color="model_size",
                         barmode="group", title="Average CO₂ Emissions (g eq.)")
        st.plotly_chart(fig_co2, use_container_width=True)

else:
    st.warning("No data or task categories available for analysis.")
