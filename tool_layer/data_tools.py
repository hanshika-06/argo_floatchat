import xarray as xr
import plotly.express as px
import os
import pandas as pd

# -------------------------------------------------
# SAFE absolute file path (project-independent)
# -------------------------------------------------

CURRENT_FILE = os.path.abspath(__file__)
TOOL_LAYER_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_ROOT = os.path.dirname(TOOL_LAYER_DIR)

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "indian_ocean_index.nc")

# -------------------------------------------------
# Load NetCDF dataset
# -------------------------------------------------
def load_dataset():
    """
    Loads the NetCDF dataset using xarray.
    """
    return xr.open_dataset(DATA_PATH)

# -------------------------------------------------
# Dataset summary (numeric variables only)
# -------------------------------------------------
def get_summary(ds):
    """
    Computes mean values for numeric variables only.
    Used for KPIs and chatbot summary queries.
    """
    summary = {}

    for var in ds.data_vars:
        # Skip non-numeric variables
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

# -------------------------------------------------
# Vertical profile plot (Pressure vs Variable)
# -------------------------------------------------
def plot_vertical_profile(ds, variable):
    """
    Plots an ARGO-style vertical profile using pressure.
    """
    df = ds.to_dataframe().reset_index()

    # Safety check
    if "pressure" not in df.columns or variable not in df.columns:
        return None

    fig = px.line(
        df,
        y="pressure",
        x=variable,
        title=f"{variable.upper()} Vertical Profile"
    )

    # Oceanographic convention: surface at top
    fig.update_yaxes(
        autorange="reversed",
        title="Pressure (dbar)"
    )

    fig.update_xaxes(title=variable.upper())

    return fig

# -------------------------------------------------
# Time-series trend (optional support)
# -------------------------------------------------
def plot_trend(ds, variable):
    """
    Plots time-series trend if time coordinate exists.
    """
    if "time" not in ds.coords:
        return None

    df = ds.to_dataframe().reset_index()

    return px.line(
        df,
        x="time",
        y=variable,
        title=f"{variable.upper()} Trend Over Time"
    )

# -------------------------------------------------
# Yearly average (optional support)
# -------------------------------------------------
def yearly_average(ds, variable):
    """
    Computes yearly averages if time coordinate exists.
    """
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

# ---------------------------------------
# Data-driven condition summary
# ---------------------------------------
def compute_ocean_condition(ds):
    summary = {}

    if "pressure" not in ds:
        return summary

    surface = ds.where(ds["pressure"] <= 100, drop=True)
    deep = ds.where(ds["pressure"] >= 1000, drop=True)

    for var in ["temperature", "oxygen", "salinity"]:
        if var in ds:
            try:
                summary[var] = {
                    "surface": float(surface[var].mean().values),
                    "deep": float(deep[var].mean().values)
                }
            except Exception:
                pass

    return summary

def plot_location_map_from_csv():
    import pandas as pd
    import plotly.express as px
    import os

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH = os.path.join(PROJECT_ROOT, "data", "indian_ocean_index.csv")

    # Load CSV
    df = pd.read_csv(CSV_PATH)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Safety check
    if "latitude" not in df.columns or "longitude" not in df.columns:
        return None

    # Drop invalid rows
    df = df.dropna(subset=["latitude", "longitude"])

    # Plot float locations as POINTS
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        title="ARGO Float Locations",
        opacity=0.7,
        height=500
    )

    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="rgb(243,243,243)"
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig

