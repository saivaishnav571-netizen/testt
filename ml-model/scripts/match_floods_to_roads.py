import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

FLOOD_FILE = (
    BASE_DIR / "data" / "raw" / "flood"
    / "INDIA_FLOOD_INVENTORY_V3.geojson"
)

ROAD_FILE = (
    BASE_DIR / "data" / "processed" / "terrain"
    / "road_terrain_final.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "flood"
OUTPUT_FILE = OUTPUT_DIR / "road_flood_features.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 1. LOAD FLOOD INVENTORY
# ---------------------------------------------------------

print("Loading flood inventory...")

floods = gpd.read_file(FLOOD_FILE)

print(f"Total flood events: {len(floods)}")
print(f"Flood CRS: {floods.crs}")


# ---------------------------------------------------------
# 2. LOAD ROADS
# ---------------------------------------------------------

print("\nLoading roads...")

roads = pd.read_csv(
    ROAD_FILE,
    low_memory=False
)

print(f"Total roads: {len(roads)}")


# ---------------------------------------------------------
# 3. CREATE ROAD GEODATAFRAME
# ---------------------------------------------------------

print("\nCreating road GeoDataFrame...")

roads_gdf = gpd.GeoDataFrame(
    roads.copy(),
    geometry=gpd.points_from_xy(
        roads["longitude"],
        roads["latitude"]
    ),
    crs="EPSG:4326"
)


# ---------------------------------------------------------
# 4. FILTER FLOODS TO NORTHEAST INDIA
# ---------------------------------------------------------

print("\nFiltering flood events to Northeast study area...")

min_lon = 88.0
max_lon = 97.5
min_lat = 21.5
max_lat = 29.5

floods_ner = floods.cx[
    min_lon:max_lon,
    min_lat:max_lat
].copy()

print(
    f"Flood events inside study area: "
    f"{len(floods_ner)}"
)


# ---------------------------------------------------------
# 5. PROJECT TO METRIC CRS
# ---------------------------------------------------------

print("\nProjecting data to metric CRS...")

roads_metric = roads_gdf.to_crs("EPSG:32645")
floods_metric = floods_ner.to_crs("EPSG:32645")


# ---------------------------------------------------------
# 6. DIRECT FLOOD EXPOSURE
# ---------------------------------------------------------

print("\nCalculating direct flood exposure...")

direct_join = gpd.sjoin(
    roads_metric[["road_id", "geometry"]],
    floods_metric[["FID", "geometry"]],
    how="left",
    predicate="within"
)

direct_counts = (
    direct_join
    .dropna(subset=["FID"])
    .groupby("road_id")
    .size()
    .rename("flood_direct_count")
)

result = roads[["road_id"]].copy()

result = result.merge(
    direct_counts,
    on="road_id",
    how="left"
)

result["flood_direct_count"] = (
    result["flood_direct_count"]
    .fillna(0)
    .astype(int)
)

result["flood_direct_exposure"] = (
    result["flood_direct_count"] > 0
).astype(int)

print(
    f"Directly exposed roads: "
    f"{result['flood_direct_exposure'].sum():,}"
)


# ---------------------------------------------------------
# 7. ACTUAL FLOOD POLYGON PROXIMITY
# ---------------------------------------------------------

print("\nCalculating proximity to actual flood polygons...")

# Spatial index based distance joins.
#
# IMPORTANT:
# We use the actual flood polygons here.
# We are NOT using flood centroids/representative points.

road_geometry = roads_metric[
    ["road_id", "geometry"]
]

flood_geometry = floods_metric[
    ["FID", "geometry"]
]


# ---------------------------------------------------------
# 8. FLOOD EVENTS WITHIN 5 KM
# ---------------------------------------------------------

print("\nCalculating flood events within 5 km...")

join_5km = gpd.sjoin(
    road_geometry,
    flood_geometry,
    how="left",
    predicate="dwithin",
    distance=5000
)

count_5km = (
    join_5km
    .dropna(subset=["FID"])
    .groupby("road_id")["FID"]
    .nunique()
    .rename("flood_events_5km")
)

result = result.merge(
    count_5km,
    on="road_id",
    how="left"
)

result["flood_events_5km"] = (
    result["flood_events_5km"]
    .fillna(0)
    .astype(int)
)


# ---------------------------------------------------------
# 9. FLOOD EVENTS WITHIN 10 KM
# ---------------------------------------------------------

print("\nCalculating flood events within 10 km...")

join_10km = gpd.sjoin(
    road_geometry,
    flood_geometry,
    how="left",
    predicate="dwithin",
    distance=10000
)

count_10km = (
    join_10km
    .dropna(subset=["FID"])
    .groupby("road_id")["FID"]
    .nunique()
    .rename("flood_events_10km")
)

result = result.merge(
    count_10km,
    on="road_id",
    how="left"
)

result["flood_events_10km"] = (
    result["flood_events_10km"]
    .fillna(0)
    .astype(int)
)


# ---------------------------------------------------------
# 10. FLOOD PROXIMITY FLAGS
# ---------------------------------------------------------

result["flood_nearby_5km"] = (
    result["flood_events_5km"] > 0
).astype(int)

result["flood_nearby_10km"] = (
    result["flood_events_10km"] > 0
).astype(int)


# ---------------------------------------------------------
# 11. NEAREST ACTUAL FLOOD POLYGON DISTANCE
# ---------------------------------------------------------

print("\nCalculating nearest flood polygon distance...")

nearest = gpd.sjoin_nearest(
    road_geometry,
    flood_geometry,
    how="left",
    distance_col="nearest_flood_distance_m"
)

nearest_distance = (
    nearest
    .groupby("road_id")["nearest_flood_distance_m"]
    .min()
    .rename("nearest_flood_distance_m")
)

result = result.merge(
    nearest_distance,
    on="road_id",
    how="left"
)

result["nearest_flood_distance_km"] = (
    result["nearest_flood_distance_m"] / 1000
)

result.drop(
    columns=["nearest_flood_distance_m"],
    inplace=True
)


# ---------------------------------------------------------
# 12. SAVE
# ---------------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 13. SUMMARY
# ---------------------------------------------------------

print("\n----------------------------------------")
print("FLOOD FEATURE EXTRACTION COMPLETED")
print("----------------------------------------")

print(f"Output file:")
print(OUTPUT_FILE)

print(f"\nRoads processed: {len(result):,}")

print(
    f"Direct flood exposure: "
    f"{result['flood_direct_exposure'].sum():,}"
)

print(
    f"Roads with flood event within 5 km: "
    f"{result['flood_nearby_5km'].sum():,}"
)

print(
    f"Roads with flood event within 10 km: "
    f"{result['flood_nearby_10km'].sum():,}"
)

print(
    f"Maximum events within 5 km: "
    f"{result['flood_events_5km'].max()}"
)

print(
    f"Maximum events within 10 km: "
    f"{result['flood_events_10km'].max()}"
)

print(
    f"Nearest flood distance: "
    f"{result['nearest_flood_distance_km'].min():.3f} km "
    f"to "
    f"{result['nearest_flood_distance_km'].max():.3f} km"
)