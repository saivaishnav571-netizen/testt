import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/processed/master/road_risk_labeled.csv"

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print("SPATIAL VALIDATION")
print("=" * 70)

print(f"\nTotal roads: {len(df):,}")


# ============================================================
# 2. FEATURES
# ============================================================

features = [
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
    "nearest_flood_distance_km"
]

X = df[features]
y = df["risk_label"]


# ============================================================
# 3. CREATE GEOGRAPHIC GRID
# ============================================================

# Approximately 0.5 degree geographic blocks.
# Roads inside the same block stay together.

GRID_SIZE = 0.5

df["grid_lat"] = np.floor(df["latitude"] / GRID_SIZE)
df["grid_lon"] = np.floor(df["longitude"] / GRID_SIZE)

df["grid_id"] = (
    df["grid_lat"].astype(str)
    + "_"
    + df["grid_lon"].astype(str)
)

groups = df["grid_id"]

print(f"Unique geographic blocks: {groups.nunique():,}")


# ============================================================
# 4. RANDOMLY SELECT GEOGRAPHIC BLOCKS FOR TESTING
# ============================================================

rng = np.random.RandomState(42)

unique_blocks = groups.unique()

rng.shuffle(unique_blocks)

test_block_count = int(len(unique_blocks) * 0.20)

test_blocks = set(unique_blocks[:test_block_count])

test_mask = groups.isin(test_blocks)

train_mask = ~test_mask


X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]


print(f"\nTraining roads: {len(X_train):,}")
print(f"Testing roads : {len(X_test):,}")

print(f"Training blocks: {groups[train_mask].nunique():,}")
print(f"Testing blocks : {groups[test_mask].nunique():,}")


# ============================================================
# 5. TRAIN NEW RANDOM FOREST
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# ============================================================
# 6. PREDICTIONS
# ============================================================

train_pred = model.predict(X_train)
test_pred = model.predict(X_test)


# ============================================================
# 7. METRICS
# ============================================================

train_accuracy = accuracy_score(y_train, train_pred)
test_accuracy = accuracy_score(y_test, test_pred)

train_f1 = f1_score(y_train, train_pred, average="macro")
test_f1 = f1_score(y_test, test_pred, average="macro")


print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

print(
    f"\nTraining Accuracy : "
    f"{train_accuracy:.4f} ({train_accuracy * 100:.2f}%)"
)

print(
    f"Spatial Test Accuracy : "
    f"{test_accuracy:.4f} ({test_accuracy * 100:.2f}%)"
)

print(f"\nTraining Macro F1 : {train_f1:.4f}")
print(f"Spatial Test Macro F1 : {test_f1:.4f}")


# ============================================================
# 8. CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 70)
print("SPATIAL TEST CLASSIFICATION REPORT")
print("=" * 70)

print(
    classification_report(
        y_test,
        test_pred,
        digits=4
    )
)


# ============================================================
# 9. CONFUSION MATRIX
# ============================================================

labels = [
    "LOW",
    "MODERATE",
    "HIGH",
    "VERY HIGH"
]

cm = confusion_matrix(
    y_test,
    test_pred,
    labels=labels
)

print("\n" + "=" * 70)
print("SPATIAL CONFUSION MATRIX")
print("=" * 70)

print("\nRows = Actual")
print("Columns = Predicted\n")

print(
    pd.DataFrame(
        cm,
        index=[f"Actual {x}" for x in labels],
        columns=[f"Predicted {x}" for x in labels]
    )
)


# ============================================================
# 10. SAVE SPATIAL MODEL
# ============================================================

MODEL_PATH = "models/road_risk_random_forest_spatial.pkl"

joblib.dump(model, MODEL_PATH)

print("\nSpatial model saved to:")
print(MODEL_PATH)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)