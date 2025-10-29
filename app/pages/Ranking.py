import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# ---- CONFIG ----
st.set_page_config(page_title="🏁 Model Ranking by Use Case", page_icon="🏁", layout="wide")

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
st.title("🏁 Which Model for Which Use Case")
st.caption("Ranking of models by task category based on a weighted score (quality, latency, energy).")
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
            for col in ["quality", "latency_s", "energy_wh"]:
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

if df.empty:
    st.warning("⚠️ No data available.")
    st.stop()

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

df["task_category"] = df["task_id"].apply(categorize_task)

# ---- AGGREGATION ----
agg = df.groupby(["task_category", "model", "model_size"], as_index=False).agg(
    quality_mean=("quality", "mean"),
    latency_mean=("latency_s", "mean"),
    energy_mean=("energy_wh", "mean")
).round(3)

# ---- NORMALIZATION ----
def normalize(series, invert=False):
    if series.max() == series.min():
        return np.ones_like(series)
    n = (series - series.min()) / (series.max() - series.min())
    return 1 - n if invert else n

# ---- WEIGHTING SYSTEM ----
st.sidebar.header("⚙️ Criteria Weights")
st.sidebar.caption("Distribute a total of 1.0 across the metrics (sum must not exceed 1.0).")

remaining = 1.0

# Quality weight
w_quality = st.sidebar.slider("Quality Weight", 0.0, remaining, 0.5, 0.01)
remaining -= w_quality

# Latency weight
w_latency = st.sidebar.slider("Latency Weight", 0.0, remaining, min(0.25, remaining), 0.01)
remaining -= w_latency

# Energy weight
w_energy = st.sidebar.slider("Energy Weight", 0.0, remaining, min(0.25, remaining), 0.01)
remaining -= w_energy

# Display total weight
total_weight = w_quality + w_latency + w_energy
st.sidebar.markdown(f"**Current total:** `{total_weight:.2f}` / 1.0")
if remaining > 0:
    st.sidebar.markdown(f"🪙 **Remaining weight available:** `{remaining:.2f}`")
else:
    st.sidebar.markdown("✅ All weights allocated.")

# Validation
if total_weight > 1.001:
    st.sidebar.error("⚠️ Total weight exceeds 1.0. Please adjust the sliders.")
    st.stop()

# ---- SCORE CALCULATION ----
agg["score"] = (
    w_quality * normalize(agg["quality_mean"]) +
    w_latency * normalize(agg["latency_mean"], invert=True) +
    w_energy * normalize(agg["energy_mean"], invert=True)
).round(3)

# ---- RANKING DISPLAY ----
st.subheader("🏆 Best Model per Task Category")

for cat in agg["task_category"].unique():
    sub = agg[agg["task_category"] == cat].sort_values("score", ascending=False)
    best = sub.iloc[0]

    st.markdown(f"### 🎯 {cat}")
    st.success(
        f"**{best['model']} ({best['model_size']})** is the most suitable model "
        f"for this category (score **{best['score']:.3f}**)  \n"
        f"• Quality: {best['quality_mean']:.2f}  |  "
        f"Latency: {best['latency_mean']:.2f}s  |  "
        f"Energy: {best['energy_mean']:.3f} wh"
    )

    # ---- Top 5 Chart ----
    top5 = sub.head(5)
    fig = px.bar(
        top5,
        x="score",
        y="model",
        color="model_size",
        orientation="h",
        title=f"Top 5 Models for {cat}",
        text="score"
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis_categoryorder="total ascending", height=400)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🔍 Full Details"):
        st.dataframe(sub.reset_index(drop=True), use_container_width=True)

    st.divider()

# ---- EXPORT ----
st.download_button(
    "📤 Export full ranking (CSV)",
    agg.to_csv(index=False).encode("utf-8"),
    "ranking_by_use_case.csv",
    "text/csv",
    key="download-usecase"
)
