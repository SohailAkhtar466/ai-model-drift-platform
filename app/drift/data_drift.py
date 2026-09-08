from pathlib import Path
from typing import Dict, Any

import json
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BASELINE_PATH = (
    PROJECT_ROOT
    / "model"
    / "reference_baseline.json"
)


FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]


# ---------------------------------------------------------
# Drift thresholds
# ---------------------------------------------------------

PSI_WARNING_THRESHOLD = 0.10
PSI_DRIFT_THRESHOLD = 0.20

KS_P_VALUE_THRESHOLD = 0.05


# ---------------------------------------------------------
# Load baseline
# ---------------------------------------------------------

def load_baseline() -> Dict[str, Any]:

    if not BASELINE_PATH.exists():

        raise FileNotFoundError(
            f"Baseline file not found:\n"
            f"{BASELINE_PATH}"
        )

    with open(
        BASELINE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# PSI calculation
# ---------------------------------------------------------

def calculate_psi(
    reference_distribution,
    production_distribution
):

    reference = np.asarray(
        reference_distribution,
        dtype=float
    )

    production = np.asarray(
        production_distribution,
        dtype=float
    )

    # Avoid division by zero / log(0)
    epsilon = 1e-10

    reference = np.clip(
        reference,
        epsilon,
        None
    )

    production = np.clip(
        production,
        epsilon,
        None
    )

    psi = np.sum(
        (
            production - reference
        )
        *
        np.log(
            production / reference
        )
    )

    return float(psi)


# ---------------------------------------------------------
# Calculate production distribution
# ---------------------------------------------------------

def calculate_production_distribution(
    series: pd.Series,
    bin_edges
):

    series = series.dropna()

    counts, _ = np.histogram(
        series,
        bins=bin_edges
    )

    total = counts.sum()

    if total == 0:

        return np.zeros(
            len(bin_edges) - 1
        )

    distribution = (
        counts / total
    )

    return distribution


# ---------------------------------------------------------
# PSI status
# ---------------------------------------------------------

def get_psi_status(psi: float) -> str:

    if psi < PSI_WARNING_THRESHOLD:

        return "NORMAL"

    if psi < PSI_DRIFT_THRESHOLD:

        return "WARNING"

    return "DRIFT"


# ---------------------------------------------------------
# KS Test
# ---------------------------------------------------------

def calculate_ks_test(
    reference_series: pd.Series,
    production_series: pd.Series
):

    reference_series = (
        reference_series
        .dropna()
    )

    production_series = (
        production_series
        .dropna()
    )

    statistic, p_value = ks_2samp(
        reference_series,
        production_series
    )

    if p_value < KS_P_VALUE_THRESHOLD:

        status = "DRIFT"

    else:

        status = "NORMAL"

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "status": status,
    }


# ---------------------------------------------------------
# Missing value drift
# ---------------------------------------------------------

def calculate_missing_value_drift(
    reference_series: pd.Series,
    production_series: pd.Series
):

    reference_missing = (
        reference_series.isna().mean()
    )

    production_missing = (
        production_series.isna().mean()
    )

    difference = (
        production_missing
        - reference_missing
    )

    return {
        "reference_percentage": float(
            reference_missing * 100
        ),

        "production_percentage": float(
            production_missing * 100
        ),

        "difference_percentage": float(
            difference * 100
        ),
    }


# ---------------------------------------------------------
# Analyze one feature
# ---------------------------------------------------------

def analyze_feature(
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame,
    feature: str,
    baseline: Dict[str, Any]
):

    feature_baseline = (
        baseline["features"][feature]
    )

    # -----------------------------------------------------
    # Production distribution
    # -----------------------------------------------------

    production_distribution = (
        calculate_production_distribution(
            production_df[feature],
            feature_baseline["bin_edges"]
        )
    )

    reference_distribution = (
        feature_baseline["distribution"]
    )

    # -----------------------------------------------------
    # PSI
    # -----------------------------------------------------

    psi = calculate_psi(
        reference_distribution,
        production_distribution
    )

    psi_status = get_psi_status(
        psi
    )

    # -----------------------------------------------------
    # KS Test
    # -----------------------------------------------------

    ks_result = calculate_ks_test(
        reference_df[feature],
        production_df[feature]
    )

    # -----------------------------------------------------
    # Missing values
    # -----------------------------------------------------

    missing_result = (
        calculate_missing_value_drift(
            reference_df[feature],
            production_df[feature]
        )
    )

    return {

        "psi": psi,

        "psi_status": psi_status,

        "ks_test": ks_result,

        "missing_values": missing_result,

    }


# ---------------------------------------------------------
# Analyze complete dataset
# ---------------------------------------------------------

def detect_data_drift(
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame
):

    baseline = load_baseline()

    results = {}

    for feature in FEATURES:

        if feature not in reference_df.columns:

            raise ValueError(
                f"Feature '{feature}' "
                f"missing from reference data."
            )

        if feature not in production_df.columns:

            raise ValueError(
                f"Feature '{feature}' "
                f"missing from production data."
            )

        results[feature] = analyze_feature(
            reference_df,
            production_df,
            feature,
            baseline
        )

    return results