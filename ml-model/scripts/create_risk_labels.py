import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_master_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_labeled.csv"
)


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

print("Loading clean master dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Roads loaded: {len(df):,}")


# ---------------------------------------------------------
# 2. PERCENTILE SCORING FUNCTION
# ---------------------------------------------------------

def percentile_score(series):
    """
    Convert a numerical feature into a 0-100
    percentile-based risk contribution.
    """

    return (
        series.rank(
            method="average",
            pct=True
        ) * 100
    )


# ---------------------------------------------------------
# 3. RAINFALL RISK
# ---------------------------------------------------------

print("\nCalculating rainfall risk...")

rain_features = [
    "rain_mean_daily_mm",
    "rain_max_daily_mm",
    "rain_max_7day_mm",
    "heavy_rain_days",
    "very_heavy_rain_days",
    "extreme_rain_days",
]

rain_scores = []

for col in rain_features:

    score = percentile_score(df[col])

    rain_scores.append(score)


df["rainfall_risk_score"] = (
    pd.concat(rain_scores, axis=1)
    .mean(axis=1)
)


# ---------------------------------------------------------
# 4. LANDSLIDE RISK
# ---------------------------------------------------------

print("Calculating landslide risk...")

landslide_features = [
    "landslide_count_5km",
    "landslide_count_10km",
]

landslide_scores = []

for col in landslide_features:

    score = percentile_score(df[col])

    landslide_scores.append(score)


# Distance works in the opposite direction:
# smaller distance = greater risk.

distance_score = (
    100 -
    percentile_score(
        df["landslide_distance_km"]
    )
)

landslide_scores.append(distance_score)


df["landslide_risk_score"] = (
    pd.concat(landslide_scores, axis=1)
    .mean(axis=1)
)


# Add direct nearby landslide exposure

df["landslide_risk_score"] = (
    0.70 * df["landslide_risk_score"]
    +
    0.30 * (
        df["landslide_nearby"] * 100
    )
)


# ---------------------------------------------------------
# 5. FLOOD RISK
# ---------------------------------------------------------

print("Calculating flood risk...")

flood_features = [
    "flood_events_5km",
    "flood_events_10km",
]

flood_scores = []

for col in flood_features:

    score = percentile_score(df[col])

    flood_scores.append(score)


# Direct historical flood exposure

flood_scores.append(
    df["flood_direct_exposure"] * 100
)


# Distance to nearest flood polygon
# Smaller distance = higher risk.

flood_distance_score = (
    100 -
    percentile_score(
        df["nearest_flood_distance_km"]
    )
)

flood_scores.append(
    flood_distance_score
)


df["flood_risk_score"] = (
    pd.concat(flood_scores, axis=1)
    .mean(axis=1)
)


# ---------------------------------------------------------
# 6. TERRAIN RISK
# ---------------------------------------------------------

print("Calculating terrain risk...")

# Slope is the primary terrain hazard indicator.
slope_score = percentile_score(
    df["slope_deg"]
)

# Very high elevation can also indicate
# mountainous terrain, but we give it lower influence.
elevation_score = percentile_score(
    df["elevation_m"]
)

df["terrain_risk_score"] = (
    0.75 * slope_score
    +
    0.25 * elevation_score
)


# ---------------------------------------------------------
# 7. OVERALL RISK SCORE
# ---------------------------------------------------------

print("\nCalculating overall risk score...")

df["overall_risk_score"] = (
    0.25 * df["rainfall_risk_score"]
    +
    0.25 * df["landslide_risk_score"]
    +
    0.35 * df["flood_risk_score"]
    +
    0.15 * df["terrain_risk_score"]
)


# Make absolutely sure score stays in 0-100 range.

df["overall_risk_score"] = (
    df["overall_risk_score"]
    .clip(0, 100)
)


# ---------------------------------------------------------
# 8. CREATE RISK LABEL
# ---------------------------------------------------------

print("Creating risk labels...")

def assign_risk(score):

    if score < 25:
        return "LOW"

    elif score < 50:
        return "MODERATE"

    elif score < 75:
        return "HIGH"

    else:
        return "VERY HIGH"


df["risk_label"] = (
    df["overall_risk_score"]
    .apply(assign_risk)
)


# ---------------------------------------------------------
# 9. CHECK RISK DISTRIBUTION
# ---------------------------------------------------------

print("\nRisk distribution:")

risk_counts = (
    df["risk_label"]
    .value_counts()
    .reindex(
        ["LOW", "MODERATE", "HIGH", "VERY HIGH"],
        fill_value=0
    )
)

print(risk_counts.to_string())


print("\nRisk percentages:")

risk_percent = (
    df["risk_label"]
    .value_counts(normalize=True)
    .reindex(
        ["LOW", "MODERATE", "HIGH", "VERY HIGH"],
        fill_value=0
    ) * 100
)

for label, percentage in risk_percent.items():

    print(
        f"{label}: {percentage:.2f}%"
    )


# ---------------------------------------------------------
# 10. SCORE STATISTICS
# ---------------------------------------------------------

print("\nRisk score statistics:")

print(
    df["overall_risk_score"]
    .describe()
    .to_string()
)


# ---------------------------------------------------------
# 11. SAVE
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("RISK LABELING COMPLETED")
print("----------------------------------------")

print("Output:")
print(OUTPUT_FILE)

print(
    f"\nRows: {len(df):,}"
)

print(
    f"Columns: {len(df.columns)}"
)