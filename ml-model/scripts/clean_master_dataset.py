import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_master.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_master_clean.csv"
)


# ---------------------------------------------------------
# 1. LOAD MASTER DATASET
# ---------------------------------------------------------

print("Loading master dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Original rows: {len(df):,}")
print(f"Original columns: {len(df.columns)}")


# ---------------------------------------------------------
# 2. REMOVE DUPLICATE ROAD ATTRIBUTE COLUMNS
# ---------------------------------------------------------

columns_to_remove = [
    # Rainfall duplicates
    "road_type_rain",
    "name_rain",
    "ref_rain",
    "surface_rain",
    "lanes_rain",
    "maxspeed_rain",
    "oneway_rain",
    "bridge_rain",
    "tunnel_rain",
    "latitude_rain",
    "longitude_rain",
    "elevation_m_rain",
    "slope_deg_rain",
    "terrain_imputed_rain",
    "terrain_source_rain",

    # Landslide duplicates
    "road_type_landslide",
    "name_landslide",
    "ref_landslide",
    "surface_landslide",
    "lanes_landslide",
    "maxspeed_landslide",
    "oneway_landslide",
    "bridge_landslide",
    "tunnel_landslide",
    "latitude_landslide",
    "longitude_landslide",
    "elevation_m_landslide",
    "slope_deg_landslide",
    "terrain_imputed_landslide",
    "terrain_source_landslide",
]

# Only remove columns that actually exist
columns_to_remove = [
    col for col in columns_to_remove
    if col in df.columns
]

df.drop(
    columns=columns_to_remove,
    inplace=True
)

print(
    f"Removed duplicate columns: "
    f"{len(columns_to_remove)}"
)


# ---------------------------------------------------------
# 3. FIX NUMERICAL TERRAIN MISSING VALUES
# ---------------------------------------------------------

print("\nChecking terrain values...")

terrain_columns = [
    "elevation_m",
    "slope_deg"
]

for col in terrain_columns:

    missing_before = df[col].isna().sum()

    if missing_before > 0:

        print(
            f"{col}: {missing_before} missing values"
        )

        # Use median because these are continuous
        # geographical measurements.
        median_value = df[col].median()

        df[col] = df[col].fillna(median_value)

        print(
            f"Filled using median: "
            f"{median_value:.4f}"
        )


# ---------------------------------------------------------
# 4. CONVERT ENVIRONMENTAL FEATURES TO NUMERIC
# ---------------------------------------------------------

numeric_columns = [
    "elevation_m",
    "slope_deg",
    "rain_mean_daily_mm",
    "rain_max_daily_mm",
    "rain_max_7day_mm",
    "heavy_rain_days",
    "very_heavy_rain_days",
    "extreme_rain_days",
    "landslide_distance_km",
    "landslide_count_5km",
    "landslide_count_10km",
    "landslide_nearby",
    "flood_direct_count",
    "flood_direct_exposure",
    "flood_events_5km",
    "flood_events_10km",
    "flood_nearby_5km",
    "flood_nearby_10km",
    "nearest_flood_distance_km",
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ---------------------------------------------------------
# 5. CHECK ROAD IDS
# ---------------------------------------------------------

print("\nChecking road IDs...")

print(
    f"Unique road IDs: "
    f"{df['road_id'].nunique():,}"
)

print(
    f"Duplicate road IDs: "
    f"{df['road_id'].duplicated().sum():,}"
)


# ---------------------------------------------------------
# 6. CHECK REMAINING MISSING VALUES
# ---------------------------------------------------------

print("\nRemaining missing values:")

missing = df.isna().sum()

missing = missing[
    missing > 0
].sort_values(
    ascending=False
)

if len(missing) == 0:

    print("No missing values.")

else:

    print(missing.to_string())


# ---------------------------------------------------------
# 7. CHECK DATASET SIZE
# ---------------------------------------------------------

print("\nFinal dataset shape:")

print(
    f"Rows: {df.shape[0]:,}"
)

print(
    f"Columns: {df.shape[1]:,}"
)


# ---------------------------------------------------------
# 8. SAVE CLEAN DATASET
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("CLEAN MASTER DATASET CREATED")
print("----------------------------------------")

print("Output:")
print(OUTPUT_FILE)

print(
    f"\nFinal rows: {len(df):,}"
)

print(
    f"Final columns: {len(df.columns)}"
)