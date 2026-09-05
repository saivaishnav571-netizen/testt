import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


# ============================================================
# PATHS
# ============================================================

ROAD_FILE = (
    r"data\processed\terrain\road_terrain_final.csv"
)

LANDSLIDE_FILE = (
    r"data\processed\landslide\landslide_inventory.csv"
)

OUTPUT_FILE = (
    r"data\processed\landslide\road_landslide_features.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("LOADING DATA")
print("=" * 60)

roads = pd.read_csv(
    ROAD_FILE,
    low_memory=False
)

landslides = pd.read_csv(
    LANDSLIDE_FILE,
    low_memory=False
)

print(f"Roads:       {len(roads):,}")
print(f"Landslides:  {len(landslides):,}")


# ============================================================
# CLEAN COORDINATES
# ============================================================

for df in [roads, landslides]:

    df["latitude"] = pd.to_numeric(
        df["latitude"]
        if "latitude" in df.columns
        else df["Latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"]
        if "longitude" in df.columns
        else df["Longitude"],
        errors="coerce"
    )


# ============================================================
# KEEP ONLY VALID COORDINATES
# ============================================================

roads = roads[
    roads["latitude"].between(-90, 90)
    &
    roads["longitude"].between(-180, 180)
].copy()

landslides = landslides[
    landslides["latitude"].between(6, 38.5)
    &
    landslides["longitude"].between(66, 100.5)
].copy()


print()
print(f"Valid roads:       {len(roads):,}")
print(f"Valid landslides:  {len(landslides):,}")


# ============================================================
# FILTER LANDSLIDES TO NORTHEAST INDIA AREA
# ============================================================

print()
print("=" * 60)
print("FILTERING NORTHEAST INDIA LANDSLIDES")
print("=" * 60)

# Your road dataset defines the actual study area.
# Add a small geographic buffer so boundary landslides are retained.

min_lat = roads["latitude"].min() - 0.5
max_lat = roads["latitude"].max() + 0.5
min_lon = roads["longitude"].min() - 0.5
max_lon = roads["longitude"].max() + 0.5

landslides = landslides[
    landslides["latitude"].between(
        min_lat,
        max_lat
    )
    &
    landslides["longitude"].between(
        min_lon,
        max_lon
    )
].copy()

print(
    f"Landslides inside study area: "
    f"{len(landslides):,}"
)


# ============================================================
# CONVERT LAT/LON TO 3D UNIT SPHERE
# ============================================================

def latlon_to_xyz(lat, lon):

    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)

    return np.column_stack((x, y, z))


road_xyz = latlon_to_xyz(
    roads["latitude"].values,
    roads["longitude"].values
)

landslide_xyz = latlon_to_xyz(
    landslides["latitude"].values,
    landslides["longitude"].values
)


# ============================================================
# BUILD SPATIAL INDEX
# ============================================================

print()
print("Building spatial index...")

tree = cKDTree(
    landslide_xyz
)


# ============================================================
# NEAREST LANDSLIDE
# ============================================================

print("Finding nearest landslide...")

distance_chord, _ = tree.query(
    road_xyz,
    k=1
)


# Convert 3D chord distance to angular distance.
angle = 2 * np.arcsin(
    np.clip(
        distance_chord / 2,
        0,
        1
    )
)


# Earth radius in km
EARTH_RADIUS_KM = 6371.0088

nearest_distance_km = (
    EARTH_RADIUS_KM * angle
)


# ============================================================
# COUNT LANDSLIDES WITHIN RADIUS
# ============================================================

def count_within_km(
    tree,
    points,
    radius_km
):

    angular_radius = (
        radius_km / EARTH_RADIUS_KM
    )

    chord_radius = (
        2 * np.sin(
            angular_radius / 2
        )
    )

    neighbours = tree.query_ball_point(
        points,
        r=chord_radius
    )

    return np.array(
        [len(x) for x in neighbours],
        dtype=np.int32
    )


print("Counting landslides within 5 km...")

count_5km = count_within_km(
    tree,
    road_xyz,
    5
)


print("Counting landslides within 10 km...")

count_10km = count_within_km(
    tree,
    road_xyz,
    10
)


# ============================================================
# CREATE FEATURES
# ============================================================

roads["landslide_distance_km"] = (
    nearest_distance_km
)

roads["landslide_count_5km"] = (
    count_5km
)

roads["landslide_count_10km"] = (
    count_10km
)

roads["landslide_nearby"] = (
    roads["landslide_count_5km"] > 0
).astype(int)


# ============================================================
# SAVE
# ============================================================

roads.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("LANDSLIDE FEATURES COMPLETE")
print("=" * 60)

print(
    f"Roads processed: "
    f"{len(roads):,}"
)

print(
    f"Roads with landslide within 5 km: "
    f"{(roads['landslide_count_5km'] > 0).sum():,}"
)

print(
    f"Roads with landslide within 10 km: "
    f"{(roads['landslide_count_10km'] > 0).sum():,}"
)

print()
print(
    roads[
        [
            "landslide_distance_km",
            "landslide_count_5km",
            "landslide_count_10km",
            "landslide_nearby"
        ]
    ].describe()
)

print()
print("Saved:")
print(OUTPUT_FILE)