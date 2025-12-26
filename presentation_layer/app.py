import sys
import os

# -------------------------------------------------
# Ensure project root is in PYTHONPATH
# -------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -------------------------------------------------
# Imports
# -------------------------------------------------
import streamlit as st
from tool_layer.data_tools import (
    load_dataset,
    plot_vertical_profile,
    get_summary,
    plot_location_map_from_csv,
    compute_ocean_condition
)
from intelligence_layer.chatbot import route_query

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="FloatChat – Indian Ocean Analysis",
    layout="wide"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🌊 FloatChat – Indian Ocean Analysis")
st.caption("Interactive ARGO-style Physical & Biogeochemical Ocean Dashboard")
st.divider()

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
ds = load_dataset()

physical_vars = ["temperature", "salinity"]
bgc_vars = ["oxygen", "nitrate", "ph", "chlorophyll", "backscattering"]
all_vars = physical_vars + bgc_vars

# -------------------------------------------------
# DATASET SUMMARY (KPIs)
# -------------------------------------------------
summary = get_summary(ds)

st.subheader("📊 Dataset Overview")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Mean Temp (°C)", f"{summary.get('temperature', 0):.2f}")
c2.metric("Mean Salinity (PSU)", f"{summary.get('salinity', 0):.2f}")
c3.metric("Mean Oxygen (µmol/kg)", f"{summary.get('oxygen', 0):.1f}")
c4.metric("Mean pH", f"{summary.get('ph', 0):.2f}")

st.divider()

# -------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------
with st.sidebar:
    st.header("🔧 Controls")

    var_category = st.radio(
        "Variable Category",
        ["Physical", "Biogeochemical"]
    )

    if var_category == "Physical":
        selected_variable = st.selectbox("Select Variable", physical_vars)
    else:
        selected_variable = st.selectbox("Select Variable", bgc_vars)

    max_depth = int(ds["pressure"].max())
    depth_range = st.slider(
        "Pressure Range (dbar)",
        0,
        max_depth,
        (0, max_depth)
    )

    compare_mode = st.checkbox("Enable Comparison Mode")

    if compare_mode:
        if var_category == "Physical":
            compare_variable = st.selectbox("Compare With", physical_vars)
        else:
            compare_variable = st.selectbox("Compare With", bgc_vars)

# -------------------------------------------------
# FILTER DATA BY DEPTH
# -------------------------------------------------
ds_filtered = ds.where(
    (ds["pressure"] >= depth_range[0]) &
    (ds["pressure"] <= depth_range[1]),
    drop=True
)

# -------------------------------------------------
# DOMAIN-SPECIFIC INSIGHTS
# -------------------------------------------------
def generate_insight(var):
    insights = {
        "temperature": "Temperature decreases with depth, indicating thermal stratification.",
        "salinity": "Salinity generally increases with depth due to water mass structure.",
        "oxygen": "Oxygen decreases with depth, suggesting limited deep-water ventilation.",
        "chlorophyll": "Chlorophyll peaks near the surface, consistent with phytoplankton growth.",
        "nitrate": "Nitrate increases with depth due to organic matter remineralization."
    }
    return insights.get(var, "Typical open-ocean vertical structure observed.")

# -------------------------------------------------
# MAIN TABS
# -------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📈 Profiles", "🌍 Map", "📘 Summary"]
)

# -------------------------------------------------
# TAB 1: PROFILE VISUALIZATION
# -------------------------------------------------
with tab1:
    st.subheader("Vertical Profile Analysis")

    if compare_mode:
        col1, col2 = st.columns(2)

        with col1:
            fig1 = plot_vertical_profile(ds_filtered, selected_variable)
            st.plotly_chart(
                fig1,
                use_container_width=True,
                key=f"profile_left_{selected_variable}"
            )
            st.info(generate_insight(selected_variable))

        with col2:
            fig2 = plot_vertical_profile(ds_filtered, compare_variable)
            st.plotly_chart(
                fig2,
                use_container_width=True,
                key=f"profile_right_{compare_variable}"
            )
            st.info(generate_insight(compare_variable))

    else:
        fig = plot_vertical_profile(ds_filtered, selected_variable)
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"profile_single_{selected_variable}"
        )
        st.info(generate_insight(selected_variable))

# -------------------------------------------------
# TAB 2: MAP
# -------------------------------------------------
with tab2:
    st.subheader("🌍 ARGO Float Locations")

    fig = plot_location_map_from_csv()
    if fig:
        st.plotly_chart(fig, use_container_width=True, key="map_tab")
    else:
        st.warning("Latitude / Longitude not available.")

# -------------------------------------------------
# TAB 3: SUMMARY & DOWNLOAD
# -------------------------------------------------
with tab3:
    st.subheader("📊 Dataset Summary")
    st.json(summary)

    csv = ds_filtered.to_dataframe().reset_index().to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered CSV",
        csv,
        "filtered_ocean_data.csv",
        "text/csv"
    )

# -------------------------------------------------
# CHATBOT SECTION (LLM-POWERED)
# -------------------------------------------------
st.divider()
st.subheader("💬 Ask FloatChat")

user_query = st.text_input(
    "Ask about the data",
    placeholder="What is the ocean condition in the Indian Ocean?"
)

if user_query:
    result = route_query(user_query)
    intent = result.get("intent")
    chat_variable = result.get("variable")

    st.caption("🧠 LLM Interpretation")
    st.json(result)

    # ---------- PROFILE ----------
    if intent == "PROFILE" and chat_variable in all_vars:
        fig = plot_vertical_profile(ds, chat_variable)
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"chat_profile_{chat_variable}"
        )
        st.info(generate_insight(chat_variable))

    # ---------- PROFILE WITH RANGE ----------
    elif intent == "PROFILE_RANGE" and chat_variable in all_vars:
        min_d = result.get("min_depth", 0)
        max_d = result.get("max_depth", 2000)

        ds_range = ds.where(
            (ds["pressure"] >= min_d) &
            (ds["pressure"] <= max_d),
            drop=True
        )

        fig = plot_vertical_profile(ds_range, chat_variable)
        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"chat_profile_range_{chat_variable}"
        )

        st.info(
            f"{chat_variable.capitalize()} shown between {min_d}–{max_d} dbar."
        )

    # ---------- MAP ----------
    elif intent == "MAP":
        fig = plot_location_map_from_csv()
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="chat_map")
        else:
            st.warning("Location data not available.")

    # ---------- CONDITION (NEW) ----------
    elif intent == "CONDITION":
        condition = compute_ocean_condition(ds)

        st.subheader("🌊 Indian Ocean Condition Summary")

        for var, values in condition.items():
            st.markdown(
                f"""
**{var.capitalize()}**
- Surface (0–100 dbar): `{values['surface']:.2f}`
- Deep (>1000 dbar): `{values['deep']:.2f}`
"""
            )

        st.success(
            "The Indian Ocean shows strong vertical stratification with warm surface waters "
            "and reduced oxygen at depth, indicating stable water masses and limited deep mixing."
        )

    # ---------- SUMMARY ----------
    elif intent == "SUMMARY":
        st.json(summary)

    else:
        st.warning(
            "I couldn't understand the question.\n\n"
            "Try:\n"
            "- What is the ocean condition?\n"
            "- Show oxygen between 0 and 500 dbar\n"
            "- Where are the floats?"
        )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()
with st.expander("🏗️ System Architecture"):
    st.markdown("""
    **Data Layer:** NetCDF + CSV  
    **Tool Layer:** Deterministic scientific functions  
    **Intelligence Layer:** LLM-based intent understanding  
    **Presentation Layer:** Streamlit + Plotly  
    """)
