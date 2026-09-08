from pathlib import Path

import pandas as pd

from app.drift.data_drift import detect_data_drift


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
# Load data
# ---------------------------------------------------------

print("Loading reference data...")

reference_df = pd.read_csv(
    REFERENCE_PATH
)


print("Loading production data...")

production_df = pd.read_csv(
    PRODUCTION_PATH
)


# ---------------------------------------------------------
# Detect drift
# ---------------------------------------------------------

print("\nRunning drift detection...")

results = detect_data_drift(
    reference_df,
    production_df
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\n" + "=" * 70)

print("DRIFT DETECTION REPORT")

print("=" * 70)


for feature, result in results.items():

    print(f"\nFeature: {feature}")

    print(
        f"PSI: "
        f"{result['psi']:.4f}"
    )

    print(
        f"PSI Status: "
        f"{result['psi_status']}"
    )

    print(
        f"KS Statistic: "
        f"{result['ks_test']['statistic']:.4f}"
    )

    print(
        f"KS P-Value: "
        f"{result['ks_test']['p_value']:.4f}"
    )

    print(
        f"KS Status: "
        f"{result['ks_test']['status']}"
    )

    print(
        f"Reference Missing: "
        f"{result['missing_values']['reference_percentage']:.2f}%"
    )

    print(
        f"Production Missing: "
        f"{result['missing_values']['production_percentage']:.2f}%"
    )

print("\n" + "=" * 70)