import pandas as pd
import numpy as np
import rasterio
from rasterio.windows import Window

# --------------------------------------------------
# Paths
# --------------------------------------------------

INPUT_FILE = r"data\processed\terrain\road_terrain.csv"

DEM_FILE = r"data\processed\dem\northeast_india_dem.tif"

SLOPE_FILE = r"data\processed\dem\northeast_india_slope.tif"

OUTPUT_FILE = r"data\processed\terrain\road_terrain_final.csv"


# --------------------------------------------------
# Load existing terrain dataset
# --------------------------------------------------

print("Loading terrain dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total roads: {len(df):,}")

df["terrain_imputed"] = 0
df["terrain_source"] = "original"


# --------------------------------------------------
# Function: find nearest valid pixel
# --------------------------------------------------

def nearest_valid(dataset, lon, lat, radius):

    row, col = dataset.index(lon, lat)

    r0 = max(0, row - radius)
    r1 = min(dataset.height, row + radius + 1)

    c0 = max(0, col - radius)
    c1 = min(dataset.width, col + radius + 1)

    data = dataset.read(
        1,
        window=Window(
            c0,
            r0,
            c1 - c0,
            r1 - r0
        )
    )

    valid = np.isfinite(data)

    if dataset.nodata is not None:
        valid &= data != dataset.nodata

    if not np.any(valid):
        return None

    rows, cols = np.where(valid)

    distances = (
        (rows + r0 - row) ** 2
        +
        (cols + c0 - col) ** 2
    )

    nearest = np.argmin(distances)

    return float(data[rows[nearest], cols[nearest]])


# --------------------------------------------------
# Search levels
# --------------------------------------------------

search_levels = [
    ("nearest_300m", 10),
    ("nearest_750m", 25),
    ("nearest_1.5km", 50),
    ("nearest_3km", 100),
]


# --------------------------------------------------
# Find roads with missing terrain
# --------------------------------------------------

missing = df["elevation_m"].isna()

print(f"Missing terrain initially: {missing.sum():,}")


# --------------------------------------------------
# Open DEM and slope
# --------------------------------------------------

with rasterio.open(DEM_FILE) as dem, \
     rasterio.open(SLOPE_FILE) as slope:

    for source_name, radius in search_levels:

        remaining = df.index[
            df["elevation_m"].isna()
        ]

        if len(remaining) == 0:
            break

        print()
        print(
            f"Searching {source_name}: "
            f"{len(remaining):,} roads remaining"
        )

        recovered = 0

        for idx in remaining:

            lon = df.at[idx, "longitude"]
            lat = df.at[idx, "latitude"]

            elevation = nearest_valid(
                dem,
                lon,
                lat,
                radius
            )

            slope_value = nearest_valid(
                slope,
                lon,
                lat,
                radius
            )

            # Only accept if BOTH values exist
            if elevation is not None and slope_value is not None:

                df.at[idx, "elevation_m"] = elevation
                df.at[idx, "slope_deg"] = slope_value

                df.at[idx, "terrain_imputed"] = 1
                df.at[idx, "terrain_source"] = source_name

                recovered += 1

        print(
            f"Recovered: {recovered:,}"
        )


# --------------------------------------------------
# Final statistics
# --------------------------------------------------

remaining = df["elevation_m"].isna()

print()
print("==========================================")
print("FINAL TERRAIN PROCESSING")
print("==========================================")

print(f"Total roads       : {len(df):,}")
print(
    f"Valid terrain     : "
    f"{(~remaining).sum():,}"
)
print(
    f"Still missing     : "
    f"{remaining.sum():,}"
)

print()
print("Terrain sources:")

print(
    df["terrain_source"]
    .value_counts()
)


# --------------------------------------------------
# Save final dataset
# --------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("Saved:")
print(OUTPUT_FILE)  