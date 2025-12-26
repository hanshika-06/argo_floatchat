import os
import numpy as np
import pandas as pd
import xarray as xr

# -------------------------------------------------
# 1. Get project root directory (float_simple)
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

nc_path = os.path.join(DATA_DIR, "indian_ocean_index.nc")

# -------------------------------------------------
# 2. Create synthetic depth / pressure profile
# -------------------------------------------------
num_points = 200  # vertical resolution

df = pd.DataFrame()

# Pressure / Depth (dbar ~ meters)
df["pressure"] = np.linspace(0, 2000, num_points)

# -------------------------------------------------
# 3. Core physical ocean variables
# -------------------------------------------------
np.random.seed(42)

df["temperature"] = (
    24
    - 0.015 * df["pressure"]
    + np.random.normal(0, 0.2, num_points)
)

df["salinity"] = (
    34.5
    + 0.001 * df["pressure"]
    + np.random.normal(0, 0.05, num_points)
)

# -------------------------------------------------
# 4. Biogeochemical variables
# -------------------------------------------------
df["oxygen"] = (
    250
    - 0.03 * df["pressure"]
    + np.random.normal(0, 5, num_points)
)

df["nitrate"] = (
    0.5
    + 0.01 * df["pressure"]
    + np.random.normal(0, 0.2, num_points)
)

df["ph"] = (
    8.1
    - 0.0005 * df["pressure"]
    + np.random.normal(0, 0.01, num_points)
)

df["chlorophyll"] = (
    np.exp(-df["pressure"] / 200)
    + np.random.normal(0, 0.05, num_points)
)

df["backscattering"] = (
    np.exp(-df["pressure"] / 300)
    + np.random.normal(0, 0.02, num_points)
)

# -------------------------------------------------
# 5. Convert DataFrame → xarray Dataset
# -------------------------------------------------
ds = xr.Dataset(
    data_vars={
        "temperature": ("pressure", df["temperature"].values),
        "salinity": ("pressure", df["salinity"].values),
        "oxygen": ("pressure", df["oxygen"].values),
        "nitrate": ("pressure", df["nitrate"].values),
        "ph": ("pressure", df["ph"].values),
        "chlorophyll": ("pressure", df["chlorophyll"].values),
        "backscattering": ("pressure", df["backscattering"].values),
    },
    coords={
        "pressure": df["pressure"].values
    },
    attrs={
        "region": "Indian Ocean",
        "source": "Synthetic ARGO-like profile",
        "institution": "FloatChat Project",
        "pressure_units": "dbar"
    }
)

# -------------------------------------------------
# 6. Save NetCDF file
# -------------------------------------------------
ds.to_netcdf(nc_path)

print("✅ NetCDF file generated successfully at:")
print(nc_path)
