import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
import io

st.set_page_config(page_title="Tariff Bubble Simulator", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
DEFAULT_DATA_PATH = RESULTS_DIR / "tariff_sensitivity_comparison.csv"

st.title("Tariff Bubble Simulator (Easy Mode)")
st.caption("One-slider learning tool: move tariff up or down and watch category bubbles change.")

st.info(
    "**CPI** = average prices people pay.\n\n"
    "**Tariff** = tax on imported goods.\n\n"
    "Bigger bubble means bigger estimated price effect in that category."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Data Source")


@st.cache_data(show_spinner=False)
def read_csv_from_path(path_str: str) -> pd.DataFrame:
    return pd.read_csv(path_str)


@st.cache_data(show_spinner=False)
def read_csv_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))


def load_sensitivity_data() -> tuple[pd.DataFrame, str]:
    candidate_paths = [
        DEFAULT_DATA_PATH,
        BASE_DIR / "tariff_sensitivity_comparison.csv",
        BASE_DIR / "figures" / "tariff_sensitivity_comparison.csv",
    ]

    for path in candidate_paths:
        if path.exists():
            return read_csv_from_path(str(path)), str(path.relative_to(BASE_DIR))

    uploaded = st.sidebar.file_uploader("Upload sensitivity CSV", type=["csv"])
    if uploaded is not None:
        return read_csv_from_bytes(uploaded.getvalue()), f"uploaded CSV ({uploaded.name})"

    demo = pd.DataFrame(
        {
            "Category": [
                "Transportation",
                "Food",
                "Housing",
                "Apparel",
                "Medical",
                "All Other Services Goods",
            ],
            "Pre-Model Correlation": [0.12, 0.08, 0.03, 0.1, 0.02, 0.06],
            "Post-Model Importance (RF)": [0.28, 0.21, 0.18, 0.14, 0.08, 0.11],
        }
    )
    return demo, "built-in demo dataset"


raw, data_source = load_sensitivity_data()
st.caption(f"Data source: **{data_source}**")

if raw.columns[0].startswith("Unnamed") or raw.columns[0] == "":
    raw = raw.rename(columns={raw.columns[0]: "Category"})

needed_cols = ["Category", "Pre-Model Correlation", "Post-Model Importance (RF)"]
missing = [col for col in needed_cols if col not in raw.columns]
if missing:
    st.error(f"Missing required columns in data: {missing}")
    st.stop()

df = raw[needed_cols].copy()
df["Category"] = df["Category"].astype(str)
df["Pre-Model Correlation"] = pd.to_numeric(df["Pre-Model Correlation"], errors="coerce").fillna(0.0)
df["Post-Model Importance (RF)"] = pd.to_numeric(df["Post-Model Importance (RF)"], errors="coerce").fillna(0.0)

emoji_map = {
    "Transportation": "🚗",
    "Food": "🍎",
    "Housing": "🏠",
    "Apparel": "👕",
    "Medical": "🏥",
    "All Other Services Goods": "🧰",
}

display_name_map = {
    "All Other Services Goods": "Services",
}

color_map = {
    "Transportation": "#1f77b4",
    "Food": "#2ca02c",
    "Housing": "#9467bd",
    "Apparel": "#ff7f0e",
    "Medical": "#d62728",
    "All Other Services Goods": "#17becf",
}

direction_color_map = {
    "positive": "#2ca02c",
    "negative": "#d62728",
    "neutral": "#7f7f7f",
}

positions = {
    "Food": (0.0, 1.0),
    "Apparel": (1.0, 1.0),
    "Transportation": (2.0, 1.0),
    "Housing": (0.3, 0.0),
    "Medical": (1.3, 0.0),
    "All Other Services Goods": (2.3, 0.0),
}

st.sidebar.header("Adjust Tariff")
tariff_change = st.sidebar.slider(
    "Tariff change (%)",
    min_value=-10.0,
    max_value=10.0,
    value=2.0,
    step=0.5,
)

neutral_threshold = 0.02
sign = np.sign(df["Pre-Model Correlation"]).astype(float)
sign[np.abs(df["Pre-Model Correlation"]) < neutral_threshold] = 0.0

df["Estimated CPI change (pp)"] = tariff_change * df["Post-Model Importance (RF)"] * sign
df["Abs impact"] = df["Estimated CPI change (pp)"].abs()

max_tariff_magnitude = max(abs(-10.0), abs(10.0))
max_sensitivity = df["Post-Model Importance (RF)"].max()
max_possible_impact = max_tariff_magnitude * max_sensitivity

if max_possible_impact > 0:
    impact_scale = (df["Abs impact"] / max_possible_impact).clip(0.0, 1.0)
    df["Bubble size"] = 40 + impact_scale * 120
else:
    df["Bubble size"] = 40

fig = go.Figure()

for _, row in df.iterrows():
    category = row["Category"]
    x, y = positions.get(category, (0.0, 0.0))
    display_name = display_name_map.get(category, category)
    emoji = emoji_map.get(category, "🔵")
    if row["Estimated CPI change (pp)"] > 0:
        color = direction_color_map["positive"]
    elif row["Estimated CPI change (pp)"] < 0:
        color = direction_color_map["negative"]
    else:
        color = direction_color_map["neutral"]
    label = f"{emoji} {display_name}<br>{row['Estimated CPI change (pp)']:+.2f} pp"

    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            marker=dict(
                size=[row["Bubble size"]],
                color=color,
                opacity=0.85,
                line=dict(color="white", width=2),
            ),
            text=[label],
            textposition="middle center",
            textfont=dict(size=14, color="white"),
            name=display_name,
            hovertemplate=(
                f"{emoji} <b>{display_name}</b><br>"
                f"Estimated CPI change: {row['Estimated CPI change (pp)']:+.2f} pp<br>"
                f"Sensitivity (RF): {row['Post-Model Importance (RF)']:.4f}<extra></extra>"
            ),
            showlegend=True,
        )
    )

fig.update_layout(
    title="Category Bubbles: Bigger = Bigger Estimated Impact",
    height=620,
    xaxis=dict(visible=False, range=[-0.5, 2.8]),
    yaxis=dict(visible=False, range=[-0.6, 1.6]),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend_title_text="Category",
)

st.plotly_chart(fig, use_container_width=True)

avg_effect = df["Estimated CPI change (pp)"].mean()
if avg_effect > 0:
    st.success(f"Average effect right now: **+{avg_effect:.2f} pp** (price pressure up)")
elif avg_effect < 0:
    st.success(f"Average effect right now: **{avg_effect:.2f} pp** (price pressure down)")
else:
    st.success("Average effect right now: **0.00 pp** (neutral)")

table = df.copy()
table["Category"] = table["Category"].map(lambda x: f"{emoji_map.get(x, '🔵')} {display_name_map.get(x, x)}")
table = table[["Category", "Estimated CPI change (pp)", "Post-Model Importance (RF)"]]
table = table.sort_values("Estimated CPI change (pp)", ascending=False)

st.subheader("Numbers Behind the Bubbles")
st.dataframe(table, use_container_width=True)

st.markdown(
    "**How to read this:**\n"
    "- Move the slider to change tariff up/down.\n"
    "- Each bubble is one category.\n"
    "- Bigger circle = bigger estimated effect.\n"
    "- Number inside bubble = estimated CPI change in percentage points."
)
