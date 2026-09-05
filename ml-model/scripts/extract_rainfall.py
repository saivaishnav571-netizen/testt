import os
import glob
import numpy as np
import pandas as pd
import xarray as xr


# ============================================================
# PATHS
# ============================================================

ROAD_FILE = r"data\processed\terrain\road_terrain_final.csv"

RAINFALL_DIR = r"data\raw\rainfall"

OUTPUT_FILE = r"data\processed\rainfall\road_rainfall.csv"


# ============================================================
# SETTINGS
# ============================================================

START_YEAR = 2015
END_YEAR = 2024


# ============================================================
# LOAD ROADS
# ============================================================

print("=" * 60)
print("LOADING ROAD DATA")
print("=" * 60)

roads = pd.read_csv(ROAD_FILE)

roads["latitude"] = pd.to_numeric(
    roads["latitude"],
    errors="coerce"
)

roads["longitude"] = pd.to_numeric(
    roads["longitude"],
    errors="coerce"
)

print(f"Total roads: {len(roads):,}")


# ============================================================
# GET RAINFALL FILES
# ============================================================

files = []

for year in range(START_YEAR, END_YEAR + 1):

    pattern = os.path.join(
        RAINFALL_DIR,
        f"RF25_ind{year}_rfp25.nc"
    )

    matches = glob.glob(pattern)

    if not matches:
        raise FileNotFoundError(
            f"Rainfall file not found for {year}: {pattern}"
        )

    files.append(matches[0])


print()
print("Rainfall files found:")

for f in files:
    print("  ", os.path.basename(f))


# ============================================================
# LOAD AND COMBINE RAINFALL DATA
# ============================================================

print()
print("=" * 60)
print("LOADING RAINFALL DATA")
print("=" * 60)

datasets = []

for file in files:

    print(
        f"Loading {os.path.basename(file)}..."
    )

    ds = xr.open_dataset(file)

    # Keep only rainfall
    rainfall = ds["RAINFALL"]

    datasets.append(rainfall)


rain = xr.concat(
    datasets,
    dim="TIME"
)

print()
print("Combined rainfall:")
print(rain)


# ============================================================
# CLEAN INVALID VALUES
# ============================================================

print()
print("Cleaning rainfall values...")

rain = rain.where(
    np.isfinite(rain)
)


# ============================================================
# CREATE 7-DAY ROLLING RAINFALL
# ============================================================

print()
print("Calculating 7-day accumulated rainfall...")

rain_7day = (
    rain
    .rolling(TIME=7, min_periods=7)
    .sum()
)


# ============================================================
# RAINFALL STATISTICS
# ============================================================

print()
print("=" * 60)
print("CALCULATING RAINFALL STATISTICS")
print("=" * 60)

print("Mean daily rainfall...")

rain_mean = rain.mean(
    dim="TIME",
    skipna=True
)

print("Maximum daily rainfall...")

rain_max = rain.max(
    dim="TIME",
    skipna=True
)

print("Maximum 7-day rainfall...")

rain_7day_max = rain_7day.max(
    dim="TIME",
    skipna=True
)


# ============================================================
# IMD RAINFALL CATEGORIES
# ============================================================

print("Counting heavy rainfall days...")

heavy_days = (
    (rain >= 64.5)
    .sum(dim="TIME")
)

very_heavy_days = (
    (rain >= 115.6)
    .sum(dim="TIME")
)

extreme_days = (
    (rain >= 204.5)
    .sum(dim="TIME")
)


# ============================================================
# SELECT RAINFALL VALUES AT ROAD LOCATIONS
# ============================================================

print()
print("=" * 60)
print("MAPPING RAINFALL TO ROADS")
print("=" * 60)

# Create xarray coordinate arrays
road_lat = xr.DataArray(
    roads["latitude"].values,
    dims="road"
)

road_lon = xr.DataArray(
    roads["longitude"].values,
    dims="road"
)


print(
    "Finding nearest 0.25° rainfall cell "
    "for each road..."
)


road_mean = rain_mean.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)

road_max = rain_max.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)

road_7day_max = rain_7day_max.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)

road_heavy = heavy_days.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)

road_very_heavy = very_heavy_days.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)

road_extreme = extreme_days.sel(
    LATITUDE=road_lat,
    LONGITUDE=road_lon,
    method="nearest"
)


# ============================================================
# ADD FEATURES TO ROAD DATAFRAME
# ============================================================

roads["rain_mean_daily_mm"] = (
    road_mean.values
)

roads["rain_max_daily_mm"] = (
    road_max.values
)

roads["rain_max_7day_mm"] = (
    road_7day_max.values
)

roads["heavy_rain_days"] = (
    road_heavy.values
)

roads["very_heavy_rain_days"] = (
    road_very_heavy.values
)

roads["extreme_rain_days"] = (
    road_extreme.values
)


# ============================================================
# SAVE
# ============================================================

print()
print("=" * 60)
print("SAVING RESULT")
print("=" * 60)

roads.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("Saved successfully:")
print(OUTPUT_FILE)

print()
print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)

print(f"Roads processed: {len(roads):,}")

print()
print(
    roads[
        [
            "rain_mean_daily_mm",
            "rain_max_daily_mm",
            "rain_max_7day_mm",
            "heavy_rain_days",
            "very_heavy_rain_days",
            "extreme_rain_days",
        ]
    ].describe()
)

print()
print("Rainfall extraction COMPLETE.")