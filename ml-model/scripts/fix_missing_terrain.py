import pandas as pd
import numpy as np
import rasterio
from rasterio.windows import Window

ROADS_FILE = r"data\processed\terrain\road_terrain.csv"
DEM_FILE = r"data\processed\dem\northeast_india_dem.tif"

df = pd.read_csv(ROADS_FILE)

missing = df["elevation_m"].isna()

print(f"Missing roads: {missing.sum():,}")


def find_nearest_valid(dataset, lon, lat, radius):
    row, col = dataset.index(lon, lat)

    r0 = max(0, row - radius)
    r1 = min(dataset.height, row + radius + 1)
    c0 = max(0, col - radius)
    c1 = min(dataset.width, col + radius + 1)

    data = dataset.read(
        1,
        window=Window(c0, r0, c1 - c0, r1 - r0)
    )

    nodata = dataset.nodata

    valid = np.isfinite(data)

    if nodata is not None:
        valid &= data != nodata

    if not np.any(valid):
        return None

    rows, cols = np.where(valid)

    distances = (
        (rows + r0 - row) ** 2 +
        (cols + c0 - col) ** 2
    )

    nearest = np.argmin(distances)

    return float(data[rows[nearest], cols[nearest]])


radii = {
    "300m": 10,
    "750m": 25,
    "1.5km": 50,
    "3km": 100,
}


with rasterio.open(DEM_FILE) as dem:

    remaining = df.index[missing]

    for name, radius in radii.items():

        found = 0

        for idx in remaining:

            lon = df.at[idx, "longitude"]
            lat = df.at[idx, "latitude"]

            value = find_nearest_valid(
                dem,
                lon,
                lat,
                radius
            )

            if value is not None:
                found += 1

        print(
            f"{name:>6} search → "
            f"{found:,} / {len(remaining):,} found"
        )