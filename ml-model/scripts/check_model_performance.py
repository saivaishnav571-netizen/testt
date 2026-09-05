import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

DATA_PATH = "data/processed/master/road_risk_labeled.csv"
MODEL_PATH = "models/road_risk_random_forest.pkl"

df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# 2. Features used by the model
# --------------------------------------------------

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

# --------------------------------------------------
# 3. Same train/test split used during training
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# 4. Load trained model
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

# --------------------------------------------------
# 5. Predictions
# --------------------------------------------------

train_pred = model.predict(X_train)
test_pred = model.predict(X_test)

# --------------------------------------------------
# 6. Accuracy
# --------------------------------------------------

train_accuracy = accuracy_score(y_train, train_pred)
test_accuracy = accuracy_score(y_test, test_pred)

train_f1 = f1_score(y_train, train_pred, average="macro")
test_f1 = f1_score(y_test, test_pred, average="macro")

print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(f"\nTraining Accuracy : {train_accuracy:.4f} ({train_accuracy * 100:.2f}%)")
print(f"Test Accuracy     : {test_accuracy:.4f} ({test_accuracy * 100:.2f}%)")

print(f"\nTraining Macro F1 : {train_f1:.4f}")
print(f"Test Macro F1     : {test_f1:.4f}")

# --------------------------------------------------
# 7. Classification report
# --------------------------------------------------

print("\n" + "=" * 60)
print("CLASSIFICATION REPORT - TEST SET")
print("=" * 60)

print(
    classification_report(
        y_test,
        test_pred,
        digits=4
    )
)

# --------------------------------------------------
# 8. Confusion matrix
# --------------------------------------------------

labels = ["LOW", "MODERATE", "HIGH", "VERY HIGH"]

cm = confusion_matrix(
    y_test,
    test_pred,
    labels=labels
)

print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print("\nRows = Actual")
print("Columns = Predicted\n")

print(pd.DataFrame(
    cm,
    index=[f"Actual {x}" for x in labels],
    columns=[f"Predicted {x}" for x in labels]
))

print("\n" + "=" * 60)