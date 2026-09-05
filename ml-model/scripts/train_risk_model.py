import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_labeled.csv"
)

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "road_risk_random_forest.pkl"


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

print("Loading labeled dataset...")

df = pd.read_csv(
    DATA_FILE,
    low_memory=False
)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ---------------------------------------------------------
# 2. SELECT ML FEATURES
# ---------------------------------------------------------

features = [
    # Terrain
    "elevation_m",
    "slope_deg",

    # Rainfall
    "rain_mean_daily_mm",
    "rain_max_daily_mm",
    "rain_max_7day_mm",
    "heavy_rain_days",
    "very_heavy_rain_days",
    "extreme_rain_days",

    # Landslide
    "landslide_distance_km",
    "landslide_count_5km",
    "landslide_count_10km",
    "landslide_nearby",

    # Flood
    "flood_direct_count",
    "flood_direct_exposure",
    "flood_events_5km",
    "flood_events_10km",
    "flood_nearby_5km",
    "flood_nearby_10km",
    "nearest_flood_distance_km",
]


TARGET = "risk_label"


# ---------------------------------------------------------
# 3. PREPARE X AND Y
# ---------------------------------------------------------

print("\nPreparing features...")

X = df[features].copy()
y = df[TARGET].copy()

print(f"Features used: {len(features)}")
print(f"Target: {TARGET}")


# ---------------------------------------------------------
# 4. CHECK MISSING VALUES
# ---------------------------------------------------------

print("\nChecking missing values...")

missing = X.isna().sum()

missing = missing[missing > 0]

if len(missing) == 0:
    print("No missing feature values.")

else:
    print(missing.to_string())

    # Median imputation for any unexpected numerical gaps
    X = X.fillna(X.median(numeric_only=True))


# ---------------------------------------------------------
# 5. TRAIN / TEST SPLIT
# ---------------------------------------------------------

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training samples: {len(X_train):,}")
print(f"Testing samples: {len(X_test):,}")


# ---------------------------------------------------------
# 6. TRAIN RANDOM FOREST
# ---------------------------------------------------------

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

model.fit(
    X_train,
    y_train
)

print("Training completed!")


# ---------------------------------------------------------
# 7. PREDICTIONS
# ---------------------------------------------------------

print("\nGenerating predictions...")

y_pred = model.predict(X_test)


# ---------------------------------------------------------
# 8. ACCURACY
# ---------------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

macro_f1 = f1_score(
    y_test,
    y_pred,
    average="macro"
)

weighted_f1 = f1_score(
    y_test,
    y_pred,
    average="weighted"
)

print("\n----------------------------------------")
print("MODEL PERFORMANCE")
print("----------------------------------------")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print(
    f"Macro F1: {macro_f1:.4f}"
)

print(
    f"Weighted F1: {weighted_f1:.4f}"
)


# ---------------------------------------------------------
# 9. CLASSIFICATION REPORT
# ---------------------------------------------------------

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        labels=[
            "LOW",
            "MODERATE",
            "HIGH",
            "VERY HIGH"
        ],
        digits=4
    )
)


# ---------------------------------------------------------
# 10. CONFUSION MATRIX
# ---------------------------------------------------------

print("\nConfusion Matrix:")

labels = [
    "LOW",
    "MODERATE",
    "HIGH",
    "VERY HIGH"
]

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)

print(
    pd.DataFrame(
        cm,
        index=[
            f"Actual {x}"
            for x in labels
        ],
        columns=[
            f"Pred {x}"
            for x in labels
        ]
    )
)


# ---------------------------------------------------------
# 11. FEATURE IMPORTANCE
# ---------------------------------------------------------

print("\nFeature Importance:")

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print(
    importance.to_string(index=False)
)


# ---------------------------------------------------------
# 12. SAVE MODEL
# ---------------------------------------------------------

print("\nSaving model...")

joblib.dump(
    model,
    MODEL_FILE
)

print(
    f"Model saved to:\n{MODEL_FILE}"
)


# ---------------------------------------------------------
# 13. FINAL SUMMARY
# ---------------------------------------------------------

print("\n----------------------------------------")
print("RISK MODEL TRAINING COMPLETED")
print("----------------------------------------")

print(
    f"Training rows: {len(X_train):,}"
)

print(
    f"Testing rows: {len(X_test):,}"
)

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)

print(
    f"Macro F1: {macro_f1:.4f}"
)

print(
    f"Weighted F1: {weighted_f1:.4f}"
)