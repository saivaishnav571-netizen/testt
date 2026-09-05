import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_labeled.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "master"
    / "road_risk_labeled.csv"
)


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

print("Loading risk dataset...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Roads loaded: {len(df):,}")


# ---------------------------------------------------------
# 2. CALCULATE QUARTILE THRESHOLDS
# ---------------------------------------------------------

q25 = df["overall_risk_score"].quantile(0.25)
q50 = df["overall_risk_score"].quantile(0.50)
q75 = df["overall_risk_score"].quantile(0.75)

print("\nRisk-score quartile thresholds:")

print(f"25th percentile: {q25:.4f}")
print(f"50th percentile: {q50:.4f}")
print(f"75th percentile: {q75:.4f}")


# ---------------------------------------------------------
# 3. CREATE QUARTILE-BASED LABELS
# ---------------------------------------------------------

def assign_risk(score):

    if score <= q25:
        return "LOW"

    elif score <= q50:
        return "MODERATE"

    elif score <= q75:
        return "HIGH"

    else:
        return "VERY HIGH"


df["risk_label"] = (
    df["overall_risk_score"]
    .apply(assign_risk)
)


# ---------------------------------------------------------
# 4. CHECK DISTRIBUTION
# ---------------------------------------------------------

print("\nNew risk distribution:")

risk_order = [
    "LOW",
    "MODERATE",
    "HIGH",
    "VERY HIGH"
]

counts = (
    df["risk_label"]
    .value_counts()
    .reindex(
        risk_order,
        fill_value=0
    )
)

percentages = (
    df["risk_label"]
    .value_counts(normalize=True)
    .reindex(
        risk_order,
        fill_value=0
    ) * 100
)

for label in risk_order:

    print(
        f"{label:10s}: "
        f"{counts[label]:,} "
        f"({percentages[label]:.2f}%)"
    )


# ---------------------------------------------------------
# 5. SAVE
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("QUARTILE RISK LABELING COMPLETED")
print("----------------------------------------")

print(f"Output:")
print(OUTPUT_FILE)

print(f"\nRows: {len(df):,}")
print(f"Columns: {len(df.columns)}")