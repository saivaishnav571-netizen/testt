import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

TERRAIN_FILE = (
    BASE_DIR / "data" / "processed" / "terrain"
    / "road_terrain_final.csv"
)

RAINFALL_FILE = (
    BASE_DIR / "data" / "processed" / "rainfall"
    / "road_rainfall_final.csv"
)

LANDSLIDE_FILE = (
    BASE_DIR / "data" / "processed" / "landslide"
    / "road_landslide_features.csv"
)

FLOOD_FILE = (
    BASE_DIR / "data" / "processed" / "flood"
    / "road_flood_features.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "master"
OUTPUT_FILE = OUTPUT_DIR / "road_risk_master.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 1. LOAD DATASETS
# ---------------------------------------------------------

print("Loading terrain dataset...")
terrain = pd.read_csv(TERRAIN_FILE, low_memory=False)
print(f"Terrain: {len(terrain):,} rows")

print("\nLoading rainfall dataset...")
rainfall = pd.read_csv(RAINFALL_FILE, low_memory=False)
print(f"Rainfall: {len(rainfall):,} rows")

print("\nLoading landslide dataset...")
landslide = pd.read_csv(LANDSLIDE_FILE, low_memory=False)
print(f"Landslide: {len(landslide):,} rows")

print("\nLoading flood dataset...")
flood = pd.read_csv(FLOOD_FILE, low_memory=False)
print(f"Flood: {len(flood):,} rows")


# ---------------------------------------------------------
# 2. CHECK ROAD IDs
# ---------------------------------------------------------

print("\nChecking road IDs...")

datasets = {
    "terrain": terrain,
    "rainfall": rainfall,
    "landslide": landslide,
    "flood": flood
}

for name, df in datasets.items():

    print(
        f"{name}: "
        f"{df['road_id'].nunique():,} unique road IDs"
    )

    duplicates = df["road_id"].duplicated().sum()

    print(
        f"  Duplicate road IDs: {duplicates:,}"
    )


# ---------------------------------------------------------
# 3. MERGE TERRAIN + RAINFALL
# ---------------------------------------------------------

print("\nMerging terrain + rainfall...")

master = terrain.merge(
    rainfall,
    on="road_id",
    how="left",
    suffixes=("", "_rain")
)

print(f"After terrain + rainfall: {len(master):,} rows")


# ---------------------------------------------------------
# 4. MERGE LANDSLIDE
# ---------------------------------------------------------

print("\nMerging landslide features...")

master = master.merge(
    landslide,
    on="road_id",
    how="left",
    suffixes=("", "_landslide")
)

print(f"After landslide merge: {len(master):,} rows")


# ---------------------------------------------------------
# 5. MERGE FLOOD
# ---------------------------------------------------------

print("\nMerging flood features...")

master = master.merge(
    flood,
    on="road_id",
    how="left",
    suffixes=("", "_flood")
)

print(f"After flood merge: {len(master):,} rows")


# ---------------------------------------------------------
# 6. CHECK DUPLICATES AFTER MERGING
# ---------------------------------------------------------

print("\nChecking final duplicates...")

duplicate_count = master["road_id"].duplicated().sum()

print(
    f"Duplicate road IDs after merge: "
    f"{duplicate_count:,}"
)


# ---------------------------------------------------------
# 7. MISSING VALUE CHECK
# ---------------------------------------------------------

print("\nChecking missing values...")

missing = master.isnull().sum()

missing = missing[missing > 0].sort_values(
    ascending=False
)

if len(missing) == 0:

    print("No missing values found.")

else:

    print("\nColumns with missing values:")

    print(missing.to_string())


# ---------------------------------------------------------
# 8. DATASET INFORMATION
# ---------------------------------------------------------

print("\nDataset shape:")
print(
    f"Rows: {master.shape[0]:,}"
)

print(
    f"Columns: {master.shape[1]:,}"
)


# ---------------------------------------------------------
# 9. SAVE MASTER DATASET
# ---------------------------------------------------------

master.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("MASTER DATASET CREATED")
print("----------------------------------------")

print("Output:")
print(OUTPUT_FILE)

print(
    f"\nFinal rows: "
    f"{len(master):,}"
)

print(
    f"Final columns: "
    f"{len(master.columns):,}"
)