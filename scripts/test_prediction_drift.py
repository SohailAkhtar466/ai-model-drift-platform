from pathlib import Path

import pandas as pd

from app.drift.prediction_drift import (
    detect_prediction_drift,
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

REFERENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "reference.csv"
)

PRODUCTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "production.csv"
)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

print(
    "Loading reference data..."
)

reference_df = pd.read_csv(
    REFERENCE_PATH
)


print(
    "Loading production data..."
)

production_df = pd.read_csv(
    PRODUCTION_PATH
)


# ---------------------------------------------------------
# Prediction drift
# ---------------------------------------------------------

print(
    "\nRunning prediction drift detection..."
)

result = detect_prediction_drift(
    reference_df,
    production_df
)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

print("\n")
print("=" * 70)

print(
    "PREDICTION DRIFT REPORT"
)

print("=" * 70)


print(
    f"\nOverall Status: "
    f"{result['status']}"
)


print("\nPrediction Class Distribution")

print(
    "\nReference:"
)

for key, value in result[
    "class_distribution"
]["reference"].items():

    print(
        f"  Class {key}: "
        f"{value:.2%}"
    )


print(
    "\nProduction:"
)

for key, value in result[
    "class_distribution"
]["production"].items():

    print(
        f"  Class {key}: "
        f"{value:.2%}"
    )


print(
    "\nProbability Drift"
)


psi = result[
    "probability_drift"
]["psi"]


ks = result[
    "probability_drift"
]["ks_test"]


print(
    f"  PSI: "
    f"{psi['psi']:.4f}"
)


print(
    f"  PSI Status: "
    f"{psi['status']}"
)


print(
    f"  KS Statistic: "
    f"{ks['statistic']:.4f}"
)


print(
    f"  KS P-Value: "
    f"{ks['p_value']:.4f}"
)


print(
    f"  KS Status: "
    f"{ks['status']}"
)


print("\n")
print("=" * 70)