import streamlit as st 
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---- CONFIG ----
st.set_page_config(
    page_title="ComparIA – Metrics Exploration",
    page_icon="📈",
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
st.title("📈 Metrics Exploration")
st.caption("Explore relationships between model performance metrics: quality, energy, CO₂, latency, and model size.")
st.divider()

# ---- DATA LOADING ----
DATA_PATH = Path(__file__).parent.parent / "data" / "data.csv"

@st.cache_data
def load_data():
    if DATA_PATH.exists():
        try:
            df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")
            df.columns = df.columns.str.strip().str.lower()
            df.rename(columns={"co_g": "co2_g"}, inplace=True)

            # Convert numeric fields
            for col in ["quality", "latency_s", "energy_wh", "co2_g"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            return df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ No data.csv found in app/data/.")
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

# ---- SIDEBAR FILTERS ----
st.sidebar.header("⚙️ Filters")

if df.empty:
    st.warning("⚠️ No data available. Please check your data.csv file.")
    st.stop()
else:
    # 1️⃣ Model sizes
    sizes_all = sorted(df["model_size"].dropna().unique())
    size_sel = st.sidebar.multiselect("Model sizes", sizes_all, default=sizes_all)

    if len(size_sel) == 0:
        st.sidebar.warning("Select at least one model size.")
        df_filtered = df.iloc[0:0]
    else:
        df_size = df[df["model_size"].isin(size_sel)]

        # 2️⃣ Task categories
        cats_all = sorted(df_size["task_category"].dropna().unique())
        cat_sel = st.sidebar.multiselect("Task categories", cats_all, default=cats_all)

        df_size_cat = df_size[df_size["task_category"].isin(cat_sel)] if len(cat_sel) else df_size.iloc[0:0]

        # 3️⃣ Models
        models_all = sorted(df_size_cat["model"].dropna().unique())
        model_sel = st.sidebar.multiselect("Models", models_all, default=models_all)

        # 🔹 Final filter
        df_filtered = df[
            df["model_size"].isin(size_sel)
            & df["task_category"].isin(cat_sel)
            & df["model"].isin(model_sel)
        ]

# ---- VISUALIZATIONS ----
if not df_filtered.empty:
    st.subheader("📊 Exploratory Visualizations")

    # Aggregate by model
    df_agg = (
        df_filtered.groupby(["model", "model_size"], as_index=False)
        .agg({
            "quality": "mean",
            "energy_wh": "mean",
            "latency_s": "mean",
            "co2_g": "mean"
        })
        .round(3)
    )

    # --- 1ère ligne : deux graphiques côte à côte ---
    col1, col2 = st.columns(2)

    # --- 1️⃣ Quality vs Energy (line chart)
    with col1:
        st.markdown("### ⚡ Quality vs Energy Consumption (wh)")
        fig_qe = px.line(
            df_agg,
            x="quality",
            y="energy_wh",
            color="model_size",
            markers=True,
            hover_data=["model"],
            title="Average Quality vs Energy Consumption"
        )
        fig_qe.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_qe, use_container_width=True)

    # --- 2️⃣ Quality vs CO2 (line chart)
    with col2:
        st.markdown("### 🌍 Quality vs CO₂ Emissions (g eq.)")
        fig_qc = px.line(
            df_agg,
            x="quality",
            y="co2_g",
            color="model_size",
            markers=True,
            hover_data=["model"],
            title="Average Quality vs CO₂ Emissions"
        )
        fig_qc.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_qc, use_container_width=True)

    # --- 2e ligne : latence centrée ---
    st.markdown("### ⏱️ Average Latency by Model Size")
    df_lat = (
        df_filtered.groupby("model_size", as_index=False)
        .agg({"latency_s": "mean"})
        .round(2)
    )
    fig_latency = px.bar(
        df_lat,
        x="model_size",
        y="latency_s",
        color="model_size",
        text_auto=".2f",
        title="Average Latency (s) per Model Size"
    )
    fig_latency.update_traces(textfont_size=12)
    st.plotly_chart(fig_latency, use_container_width=True)

else:
    st.warning("No data matches the selected filters.")
