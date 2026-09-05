"""
Data-driven road risk prediction using pre-computed predictions from
300,814 North-East India road segments.

Uses a KDTree spatial index for O(log n) nearest-neighbor lookup so
any (lat, lon) query finds the closest real road segment and returns
its actual risk data (computed from SRTM terrain, 10-year IMD rainfall,
GSI landslide inventory, and ISRO flood inventory).
"""

import os
import math
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PREDICTIONS_CSV = os.path.join(
    os.path.dirname(__file__), "..", "data", "processed", "master",
    "road_risk_predictions.csv"
)

# ---------------------------------------------------------------------------
# Global cache (loaded once on first call)
# ---------------------------------------------------------------------------

_CACHE = {
    "tree": None,       # cKDTree over (lat, lon) in radians on unit sphere
    "df": None,         # DataFrame of predictions
    "loaded": False,
}


def _load_predictions():
    """Load the predictions CSV and build a spatial KDTree (once)."""
    if _CACHE["loaded"]:
        return

    csv_path = os.path.abspath(_PREDICTIONS_CSV)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Predictions CSV not found at: {csv_path}\n"
            "Run predict_all_roads.py first to generate predictions."
        )

    df = pd.read_csv(csv_path, low_memory=False)

    # Convert lat/lon to 3D Cartesian on unit sphere for accurate
    # nearest-neighbor search (avoids distortion at high latitudes)
    lat_rad = np.radians(df["latitude"].values)
    lon_rad = np.radians(df["longitude"].values)
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)

    coords = np.column_stack([x, y, z])
    tree = cKDTree(coords)

    _CACHE["tree"] = tree
    _CACHE["df"] = df
    _CACHE["loaded"] = True


def _query_to_cartesian(lat: float, lon: float):
    """Convert a single (lat, lon) to 3D Cartesian on unit sphere."""
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    return [
        math.cos(lat_r) * math.cos(lon_r),
        math.cos(lat_r) * math.sin(lon_r),
        math.sin(lat_r),
    ]


def _chord_to_km(chord_dist: float, earth_radius_km: float = 6371.0) -> float:
    """Convert chord distance on unit sphere to great-circle km."""
    # chord = 2 * sin(angle/2), so angle = 2 * arcsin(chord/2)
    angle = 2.0 * math.asin(min(chord_dist / 2.0, 1.0))
    return angle * earth_radius_km


# ---------------------------------------------------------------------------
# Percentile-based display metrics from real feature data
# ---------------------------------------------------------------------------

# These reference values come from the actual dataset distributions
# (computed from 300,813 road segments)
_FEATURE_RANGES = {
    # slope_deg: p5=0.39, p25=1.39, p50=2.56, p75=5.57, p95=22.06, max=63.48
    "slope_deg": {"p25": 1.39, "p50": 2.56, "p75": 5.57, "p95": 22.06, "max": 63.48},
    # rain_max_7day_mm: p25=291, p50=362, p75=512, p95=850, max=3343
    "rain_max_7day_mm": {"p25": 291.0, "p50": 362.0, "p75": 512.0, "p95": 850.0, "max": 3343.0},
    # landslide_count_5km: 0=no landslides nearby, median=0, p75=4, max=239
    "landslide_count_5km": {"p25": 0, "p50": 0, "p75": 4, "p95": 24, "max": 239},
    # landslide_distance_km: 0=on a landslide, p25=2.47, p50=7.54, p75=18.83, max=84
    "landslide_distance_km": {"p25": 2.47, "p50": 7.54, "p75": 18.83, "max": 84.02},
    # flood_direct_exposure: binary 0/1
    "flood_direct_exposure": {"max": 1},
    # nearest_flood_distance_km: 0=in flood zone, p50=0, p75=54.47, max=203
    "nearest_flood_distance_km": {"p25": 0.0, "p50": 0.0, "p75": 54.47, "max": 203.35},
}


def _compute_rainfall_pct(rain_7day: float) -> int:
    """Derive rainfall risk percentage from real rain_max_7day_mm.

    Higher 7-day rainfall = higher risk percentage.
    Scale: 0-100 based on dataset percentiles.
    """
    # Clamp to dataset range
    val = max(0.0, min(rain_7day, 3343.0))
    # Percentile-based scaling: <p25 → ~10%, p50 → ~35%, p75 → ~60%, >p95 → ~90%
    if val <= 291.0:
        return max(5, int(10 + (val / 291.0) * 15))   # 5-25%
    elif val <= 362.0:
        return int(25 + ((val - 291.0) / 71.0) * 15)   # 25-40%
    elif val <= 512.0:
        return int(40 + ((val - 362.0) / 150.0) * 20)  # 40-60%
    elif val <= 850.0:
        return int(60 + ((val - 512.0) / 338.0) * 20)  # 60-80%
    else:
        return min(95, int(80 + ((val - 850.0) / 2493.0) * 15))  # 80-95%


def _compute_landslide_pct(distance_km: float, count_5km: int) -> int:
    """Derive landslide risk percentage from real landslide proximity data.

    Closer distance + higher count = higher risk.
    """
    # Distance component: closer = higher risk (inverted)
    if distance_km <= 1.0:
        dist_score = 90
    elif distance_km <= 2.47:
        dist_score = 70
    elif distance_km <= 7.54:
        dist_score = 50
    elif distance_km <= 18.83:
        dist_score = 30
    else:
        dist_score = max(5, int(30 - (distance_km - 18.83) / 65.0 * 25))

    # Count component: more landslides nearby = higher risk
    if count_5km == 0:
        count_score = 5
    elif count_5km <= 4:
        count_score = 30
    elif count_5km <= 24:
        count_score = 60
    else:
        count_score = min(95, 60 + int((count_5km - 24) / 215.0 * 35))

    # Weighted combination
    return max(5, min(95, int(0.5 * dist_score + 0.5 * count_score)))


def _compute_flood_pct(flood_exposure: int, nearest_dist_km: float) -> int:
    """Derive flood risk percentage from real flood data.

    Direct exposure + proximity to flood zones = higher risk.
    """
    if flood_exposure >= 1:
        # Road is directly inside a historical flood polygon
        base = 65
    else:
        base = 10

    # Distance penalty: further from floods = lower risk
    if nearest_dist_km <= 0.0:
        dist_bonus = 30  # inside or touching flood zone
    elif nearest_dist_km <= 5.0:
        dist_bonus = 20
    elif nearest_dist_km <= 20.0:
        dist_bonus = 10
    elif nearest_dist_km <= 54.47:
        dist_bonus = 5
    else:
        dist_bonus = 0

    return max(5, min(95, base + dist_bonus))


def _compute_road_condition_pct(prob_low: float, slope_deg: float) -> int:
    """Derive road safety percentage. Higher = safer road.

    Based on model's LOW risk probability and actual terrain slope.
    """
    # Base from model confidence in LOW risk
    model_safety = int(prob_low * 80)

    # Slope penalty: steeper = less safe
    if slope_deg <= 2.56:
        slope_bonus = 20
    elif slope_deg <= 5.57:
        slope_bonus = 10
    elif slope_deg <= 15.0:
        slope_bonus = 0
    else:
        slope_bonus = -10

    return max(10, min(95, model_safety + slope_bonus))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_risk(lat: float, lon: float, weather_data: dict = None, route_index: int = 0):
    """
    Predict road risk by looking up the nearest real road segment from the
    pre-computed predictions dataset (300,814 NER road segments).

    Parameters
    ----------
    lat, lon : float
        Query coordinates.
    weather_data : dict, optional
        Currently unused (real historical data is already in the dataset).
        Kept for API compatibility.
    route_index : int
        Route alternate index (0=primary, 1+=alternates).
        Used to search slightly offset positions for alternate routes.

    Returns
    -------
    dict with keys: risk_level, probabilities, rainfall_pct, landslide_pct,
                    flood_pct, road_condition_pct, danger_pct, safe_pct,
                    confidence, nearest_road_distance_km
    """
    _load_predictions()

    tree = _CACHE["tree"]
    df = _CACHE["df"]

    # Query the KDTree with exact coordinates
    query_pt = _query_to_cartesian(lat, lon)
    chord_dist, idx = tree.query(query_pt)
    distance_km = _chord_to_km(chord_dist)

    # Get the matched road's data
    road = df.iloc[idx]

    risk_label = road["risk_label"]
    confidence = float(road["confidence"])
    prob_high = float(road["probability_high"])
    prob_low = float(road["probability_low"])
    prob_moderate = float(road["probability_moderate"])
    prob_very_high = float(road["probability_very_high"])

    # Map risk label to display text
    label_map = {
        "LOW": "Low Risk",
        "MODERATE": "Moderate Risk",
        "HIGH": "High Risk",
        "VERY HIGH": "Very High Risk",
    }
    risk_level = label_map.get(risk_label, "Low Risk")

    # Extract real features for display metrics
    slope = float(road["slope_deg"])
    rain_7day = float(road["rain_max_7day_mm"])
    ls_dist = float(road["landslide_distance_km"])
    ls_count = int(road["landslide_count_5km"])
    flood_exp = int(road["flood_direct_exposure"])
    flood_dist = float(road["nearest_flood_distance_km"])

    # Compute display percentages from real data
    rainfall_pct = _compute_rainfall_pct(rain_7day)
    landslide_pct = _compute_landslide_pct(ls_dist, ls_count)
    flood_pct = _compute_flood_pct(flood_exp, flood_dist)
    road_condition_pct = _compute_road_condition_pct(prob_low, slope)

    # Overall danger/safety from model probabilities
    danger_pct = int((prob_high + prob_moderate + prob_very_high) * 100)
    safe_pct = int(prob_low * 100)

    return {
        "risk_level": risk_level,
        "probabilities": [prob_high, prob_low, prob_moderate, prob_very_high],
        "confidence": round(confidence, 3),
        "rainfall_pct": rainfall_pct,
        "landslide_pct": landslide_pct,
        "flood_pct": flood_pct,
        "road_condition_pct": road_condition_pct,
        "danger_pct": danger_pct,
        "safe_pct": safe_pct,
        "nearest_road_distance_km": round(distance_km, 2),
        # Extra context for debugging/display
        "matched_road_id": int(road["road_id"]),
        "matched_road_type": road["road_type"],
        "real_features": {
            "slope_deg": round(slope, 2),
            "rain_max_7day_mm": round(rain_7day, 1),
            "landslide_distance_km": round(ls_dist, 2),
            "landslide_count_5km": ls_count,
            "flood_direct_exposure": flood_exp,
            "nearest_flood_distance_km": round(flood_dist, 2),
        },
    }
