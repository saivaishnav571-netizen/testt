import os
import numpy as np
import pandas as pd
import xarray as xr


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = r"data\processed\rainfall\road_rainfall.csv"

RAINFALL_DIR = r"data\raw\rainfall"

OUTPUT_FILE = r"data\processed\rainfall\road_rainfall_final.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING RAINFALL DATA")
print("=" * 60)

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Total roads: {len(df):,}")


# ============================================================
# FEATURES WE NEED TO FIX
# ============================================================

features = [
    "rain_mean_daily_mm",
    "rain_max_daily_mm",
    "rain_max_7day_mm",
]


# Create flag
if "rainfall_imputed" not in df.columns:
    df["rainfall_imputed"] = 0


# Find missing rows
missing = df[features].isna().any(axis=1)

print(
    f"Rows requiring rainfall recovery: "
    f"{missing.sum():,}"
)


# ============================================================
# LOAD 2015–2024 RAINFALL
# ============================================================

print()
print("=" * 60)
print("LOADING RAINFALL GRIDS")
print("=" * 60)

rainfall_arrays = []

for year in range(2015, 2025):

    filename = os.path.join(
        RAINFALL_DIR,
        f"RF25_ind{year}_rfp25.nc"
    )

    print(f"Loading {os.path.basename(filename)}...")

    ds = xr.open_dataset(filename)

    rainfall_arrays.append(
        ds["RAINFALL"]
    )


rain = xr.concat(
    rainfall_arrays,
    dim="TIME"
)

rain = rain.where(
    np.isfinite(rain)
)


# ============================================================
# CALCULATE STATISTICS
# ============================================================

print()
print("Calculating rainfall statistics...")

rain_mean = rain.mean(
    dim="TIME",
    skipna=True
)

rain_max = rain.max(
    dim="TIME",
    skipna=True
)

rain_7day = (
    rain
    .rolling(TIME=7, min_periods=7)
    .sum()
)

rain_7day_max = rain_7day.max(
    dim="TIME",
    skipna=True
)


# ============================================================
# FIND VALID GRID CELLS
# ============================================================

print()
print("Finding valid rainfall cells...")

mean_values = rain_mean.values
max_values = rain_max.values
max7_values = rain_7day_max.values

latitudes = rain_mean["LATITUDE"].values
longitudes = rain_mean["LONGITUDE"].values


# A cell is usable only if all three features exist
valid_cells = (
    np.isfinite(mean_values)
    &
    np.isfinite(max_values)
    &
    np.isfinite(max7_values)
)

valid_lat_idx, valid_lon_idx = np.where(
    valid_cells
)

valid_lats = latitudes[valid_lat_idx]
valid_lons = longitudes[valid_lon_idx]

print(
    f"Valid rainfall cells: "
    f"{len(valid_lats):,}"
)


# ============================================================
# RECOVER MISSING ROADS
# ============================================================

print()
print("=" * 60)
print("RECOVERING MISSING RAINFALL")
print("=" * 60)

missing_indices = df.index[missing]

recovered = 0


for counter, idx in enumerate(missing_indices, start=1):

    lat = df.at[idx, "latitude"]
    lon = df.at[idx, "longitude"]

    # Approximate distance in degrees.
    # Longitude is adjusted for latitude.
    lat_diff = valid_lats - lat

    lon_diff = (
        valid_lons - lon
    ) * np.cos(
        np.radians(lat)
    )

    distance_squared = (
        lat_diff ** 2
        +
        lon_diff ** 2
    )

    nearest = np.argmin(
        distance_squared
    )

    grid_lat_idx = valid_lat_idx[nearest]
    grid_lon_idx = valid_lon_idx[nearest]

    mean_value = mean_values[
        grid_lat_idx,
        grid_lon_idx
    ]

    max_value = max_values[
        grid_lat_idx,
        grid_lon_idx
    ]

    max7_value = max7_values[
        grid_lat_idx,
        grid_lon_idx
    ]

    if (
        np.isfinite(mean_value)
        and
        np.isfinite(max_value)
        and
        np.isfinite(max7_value)
    ):

        df.at[
            idx,
            "rain_mean_daily_mm"
        ] = float(mean_value)

        df.at[
            idx,
            "rain_max_daily_mm"
        ] = float(max_value)

        df.at[
            idx,
            "rain_max_7day_mm"
        ] = float(max7_value)

        df.at[
            idx,
            "rainfall_imputed"
        ] = 1

        recovered += 1

    if counter % 500 == 0:
        print(
            f"Processed {counter:,} / "
            f"{len(missing_indices):,}"
        )


# ============================================================
# FINAL CHECK
# ============================================================

print()
print("=" * 60)
print("FINAL RAINFALL CHECK")
print("=" * 60)

remaining = df[features].isna().any(axis=1)

print(f"Total roads: {len(df):,}")
print(f"Recovered: {recovered:,}")
print(f"Still missing: {remaining.sum():,}")
print(
    f"Imputed rainfall rows: "
    f"{(df['rainfall_imputed'] == 1).sum():,}"
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("Saved:")
print(OUTPUT_FILE)

print()
print("RAINALL CLEANUP COMPLETE.")