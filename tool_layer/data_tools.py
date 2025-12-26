import xarray as xr
import plotly.express as px
import os
import pandas as pd

# -----------------------------
# Build SAFE absolute file path
# -----------------------------

CURRENT_FILE = os.path.abspath(__file__)
TOOL_LAYER_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_ROOT = os.path.dirname(TOOL_LAYER_DIR)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "indian_ocean_index.nc")

# -----------------------------
# Data loading
# -----------------------------
def load_dataset():
    return xr.open_dataset(DATA_PATH)

# -----------------------------
# Dataset summary (numeric only)
# -----------------------------
def get_summary(ds):
    summary = {}

    for var in ds.data_vars:
        if ds[var].dtype.kind not in "fi":
            continue

        try:
            value = ds[var].mean(skipna=True).values
            if value.size == 1:
                summary[var] = float(value)
            else:
                summary[var] = "multi-dimensional (numeric)"
        except Exception as e:
            summary[var] = f"error: {e}"

    return summary

# -----------------------------
# Vertical profile (PRESSURE)
# -----------------------------
def plot_vertical_profile(ds, variable):
    df = ds.to_dataframe().reset_index()

    if "pressure" not in df.columns:
        return None

    fig = px.line(
        df,
        y="pressure",
        x=variable,
        title=f"{variable.upper()} Vertical Profile",
    )

    # Oceanographic convention: surface at top
    fig.update_yaxes(
        autorange="reversed",
        title="Pressure (dbar)"
    )

    fig.update_xaxes(title=variable.upper())

    return fig

# -----------------------------
# Time-series trend (SAFE)
# -----------------------------
def plot_trend(ds, variable):
    if "time" not in ds.coords:
        return None

    df = ds.to_dataframe().reset_index()

    return px.line(
        df,
        x="time",
        y=variable,
        title=f"{variable.upper()} Trend Over Time"
    )

# -----------------------------
# Yearly average (SAFE)
# -----------------------------
def yearly_average(ds, variable):
    if "time" not in ds.coords:
        return None

    df = ds.to_dataframe().reset_index()
    df["time"] = pd.to_datetime(df["time"])

    yearly = df.groupby(df["time"].dt.year)[variable].mean().reset_index()

    return px.bar(
        yearly,
        x="time",
        y=variable,
        title=f"{variable.upper()} Yearly Average"
    )
