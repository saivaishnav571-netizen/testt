import osmium
import csv
import os


PBF_FILE = "data/raw/north-eastern-zone-260901.osm.pbf"
OUTPUT_FILE = "data/processed/roads_ner.csv"


class RoadHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.roads = []

    def way(self, w):

        highway = w.tags.get("highway")

        if not highway:
            return

        allowed = {
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "service",
            "living_street",
            "road",
            "track",
            "path",
            "cycleway"
        }

        if highway not in allowed:
            return

        # Get coordinates from the road geometry
        try:
            if not w.nodes:
                return

            lats = []
            lons = []

            for node in w.nodes:
                if node.location.valid():
                    lats.append(node.lat)
                    lons.append(node.lon)

            if not lats or not lons:
                return

            # Use the average coordinate as representative point
            latitude = sum(lats) / len(lats)
            longitude = sum(lons) / len(lons)

        except Exception:
            return

        self.roads.append({
            "road_id": w.id,
            "road_type": highway,
            "name": w.tags.get("name", ""),
            "ref": w.tags.get("ref", ""),
            "surface": w.tags.get("surface", ""),
            "lanes": w.tags.get("lanes", ""),
            "maxspeed": w.tags.get("maxspeed", ""),
            "oneway": w.tags.get("oneway", ""),
            "bridge": w.tags.get("bridge", ""),
            "tunnel": w.tags.get("tunnel", ""),
            "latitude": latitude,
            "longitude": longitude
        })


print("Starting OSM road extraction...")

os.makedirs("data/processed", exist_ok=True)

handler = RoadHandler()

# Important: locations=True gives us node coordinates
handler.apply_file(
    PBF_FILE,
    locations=True
)

print(f"Total roads extracted: {len(handler.roads)}")


fieldnames = [
    "road_id",
    "road_type",
    "name",
    "ref",
    "surface",
    "lanes",
    "maxspeed",
    "oneway",
    "bridge",
    "tunnel",
    "latitude",
    "longitude"
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(handler.roads)


print(f"Saved to: {OUTPUT_FILE}")
print("DONE!")