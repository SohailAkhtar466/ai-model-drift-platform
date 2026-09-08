from pathlib import Path
from typing import Dict, Any

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

REFERENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "reference.csv"
)

BASELINE_PATH = (
    PROJECT_ROOT
    / "model"
    / "reference_baseline.json"
)


# ---------------------------------------------------------
# Features
# ---------------------------------------------------------

FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]


# ---------------------------------------------------------
# Calculate feature statistics
# ---------------------------------------------------------

def calculate_feature_statistics(
    df: pd.DataFrame,
    feature: str,
    bins: int = 10
) -> Dict[str, Any]:

    series = df[feature].dropna()

    # -----------------------------------------------------
    # Create distribution bins
    # -----------------------------------------------------

    counts, bin_edges = pd.cut(
        series,
        bins=bins,
        retbins=True,
        include_lowest=True
    )

    distribution = (
        counts
        .value_counts(sort=False)
        .values
    )

    distribution = (
        distribution / distribution.sum()
    )

    statistics = {

        "mean": float(series.mean()),

        "std": float(series.std()),

        "min": float(series.min()),

        "max": float(series.max()),

        "median": float(series.median()),

        "missing_count": int(
            df[feature].isna().sum()
        ),

        "missing_percentage": float(
            df[feature].isna().mean() * 100
        ),

        "percentile_25": float(
            series.quantile(0.25)
        ),

        "percentile_50": float(
            series.quantile(0.50)
        ),

        "percentile_75": float(
            series.quantile(0.75)
        ),

        # Distribution information
        "bin_edges": [
            float(edge)
            for edge in bin_edges
        ],

        "distribution": [
            float(value)
            for value in distribution
        ],
    }

    return statistics


# ---------------------------------------------------------
# Build complete baseline
# ---------------------------------------------------------

def build_baseline(
    df: pd.DataFrame
) -> Dict[str, Any]:

    baseline = {
        "dataset": {
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
        },

        "features": {}
    }

    for feature in FEATURES:

        if feature not in df.columns:
            raise ValueError(
                f"Feature '{feature}' "
                f"not found in dataset."
            )

        baseline["features"][feature] = (
            calculate_feature_statistics(
                df,
                feature
            )
        )

    return baseline


# ---------------------------------------------------------
# Save baseline
# ---------------------------------------------------------

def save_baseline(
    baseline: Dict[str, Any],
    output_path: Path = BASELINE_PATH
):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    import json

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            baseline,
            file,
            indent=4
        )

    print(
        f"Baseline saved to:\n{output_path}"
    )


# ---------------------------------------------------------
# Load reference dataset
# ---------------------------------------------------------

def load_reference_data() -> pd.DataFrame:

    if not REFERENCE_PATH.exists():

        raise FileNotFoundError(
            f"Reference dataset not found:\n"
            f"{REFERENCE_PATH}"
        )

    return pd.read_csv(
        REFERENCE_PATH
    )


# ---------------------------------------------------------
# Main baseline pipeline
# ---------------------------------------------------------

def create_reference_baseline():

    print("Loading reference dataset...")

    df = load_reference_data()

    print(
        f"Reference dataset shape: "
        f"{df.shape}"
    )

    print("Building baseline...")

    baseline = build_baseline(df)

    save_baseline(baseline)

    print(
        "\nBaseline generation completed successfully."
    )

    return baseline


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":

    create_reference_baseline()