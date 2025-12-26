import sys
import os

# -----------------------------
# Ensure project root is in path
# -----------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -----------------------------
# Imports
# -----------------------------
import streamlit as st
from tool_layer.data_tools import (
    load_dataset,
    get_summary,
    plot_vertical_profile
)
from intelligence_layer.llm_router import route_query

# -----------------------------
# Domain-specific ocean insights
# (MUST be defined before use)
# -----------------------------
def generate_ocean_insight(variable):
    if variable == "temperature":
        return "Temperature decreases with depth, indicating thermal stratification."
    elif variable == "oxygen":
        return "Oxygen decreases with depth, suggesting limited ventilation."
    elif variable == "chlorophyll":
        return "Chlorophyll peaks near the surface, consistent with phytoplankton growth."
    elif variable == "salinity":
        return "Salinity generally increases with depth due to water mass structure."
    else:
        return "The profile shows typical oceanic vertical structure."

# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(layout="wide")
st.title("🌊 FloatChat – Indian Ocean Analysis")

# -----------------------------
# Load dataset
# -----------------------------
ds = load_dataset()

# -----------------------------
# Dataset summary
# -----------------------------
st.subheader("📊 Dataset Summary")
summary = get_summary(ds)
st.json(summary)

# -----------------------------
# Variable categorization
# -----------------------------
physical_vars = ["temperature", "salinity"]
bgc_vars = ["oxygen", "nitrate", "ph", "chlorophyll", "backscattering"]

st.subheader("🔬 Select Variable Type")
var_type = st.radio(
    "Variable Category",
    ["Physical", "Biogeochemical"],
    horizontal=True
)

if var_type == "Physical":
    variable = st.selectbox("Select Physical Variable", physical_vars)
else:
    variable = st.selectbox("Select Biogeochemical Variable", bgc_vars)

# -----------------------------
# User query input
# -----------------------------
st.subheader("🧠 Ask a Question")
query = st.text_input(
    "Example: show trend / vertical profile / summary",
    placeholder="Type your question here..."
)

# -----------------------------
# Handle user query
# -----------------------------
if query:
    intent = route_query(query).upper()

    # Treat TREND / PROFILE / DEPTH the same (pressure-based)
    if any(k in intent for k in ["TREND", "PROFILE", "DEPTH"]):
        st.subheader(f"📉 {variable.upper()} Vertical Profile")
        fig = plot_vertical_profile(ds, variable)

        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.info(generate_ocean_insight(variable))

    elif "SUMMARY" in intent:
        st.subheader("📋 Dataset Summary")
        st.json(summary)

    else:
        st.warning(
            "❓ Could not understand the query.\n\n"
            "Try: **trend**, **vertical profile**, or **summary**"
        )
