import pandas as pd
import rasterio

# -----------------------------
# File paths
# -----------------------------
ROADS_FILE = r"D:\sihhackathon\ml-model\data\processed\roads_ner.csv"

DEM_FILE = r"D:\sihhackathon\ml-model\data\processed\dem\northeast_india_dem.tif"

SLOPE_FILE = r"D:\sihhackathon\ml-model\data\processed\dem\northeast_india_slope.tif"

OUTPUT_FILE = r"D:\sihhackathon\ml-model\data\processed\terrain\road_terrain.csv"


# -----------------------------
# Load roads
# -----------------------------
print("Loading road data...")

df = pd.read_csv(ROADS_FILE)

print(f"Loaded {len(df):,} roads")


# -----------------------------
# Prepare coordinates
# -----------------------------
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

valid = df["latitude"].notna() & df["longitude"].notna()

print(f"Valid coordinates: {valid.sum():,}")


# -----------------------------
# Extract elevation
# -----------------------------
print("Extracting elevation...")

with rasterio.open(DEM_FILE) as dem:

    coords = list(
        zip(
            df.loc[valid, "longitude"],
            df.loc[valid, "latitude"]
        )
    )

    values = list(dem.sample(coords))

    elevation = [v[0] for v in values]

df.loc[valid, "elevation_m"] = elevation


# -----------------------------
# Extract slope
# -----------------------------
print("Extracting slope...")

with rasterio.open(SLOPE_FILE) as slope:

    coords = list(
        zip(
            df.loc[valid, "longitude"],
            df.loc[valid, "latitude"]
        )
    )

    values = list(slope.sample(coords))

    slope_values = [v[0] for v in values]

df.loc[valid, "slope_deg"] = slope_values


# -----------------------------
# Handle NoData values
# -----------------------------
df.loc[df["elevation_m"] == -32767, "elevation_m"] = pd.NA
df.loc[df["slope_deg"] == -9999, "slope_deg"] = pd.NA


# -----------------------------
# Save result
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)

print()
print("======================================")
print("Terrain extraction completed!")
print("======================================")
print(f"Roads processed : {len(df):,}")
print(f"Output file     : {OUTPUT_FILE}")
print()
print(df[[
    "road_id",
    "latitude",
    "longitude",
    "elevation_m",
    "slope_deg"
]].head())