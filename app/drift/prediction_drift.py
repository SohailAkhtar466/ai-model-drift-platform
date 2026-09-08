from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

MODEL_PATH = (
    PROJECT_ROOT
    / "model"
    / "churn_model.joblib"
)


# ---------------------------------------------------------
# Model features
# ---------------------------------------------------------

FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]


# ---------------------------------------------------------
# Thresholds
# ---------------------------------------------------------

PSI_WARNING_THRESHOLD = 0.10
PSI_DRIFT_THRESHOLD = 0.20

KS_P_VALUE_THRESHOLD = 0.05


# ---------------------------------------------------------
# Load model
# ---------------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found:\n"
            f"{MODEL_PATH}"
        )

    return joblib.load(
        MODEL_PATH
    )


# ---------------------------------------------------------
# Calculate PSI
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
# PSI status
# ---------------------------------------------------------

def get_psi_status(
    psi: float
) -> str:

    if psi < PSI_WARNING_THRESHOLD:

        return "NORMAL"

    if psi < PSI_DRIFT_THRESHOLD:

        return "WARNING"

    return "DRIFT"


# ---------------------------------------------------------
# Generate predictions
# ---------------------------------------------------------

def generate_predictions(
    df: pd.DataFrame
):

    model = load_model()

    X = df[FEATURES]

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)

    return predictions, probabilities


# ---------------------------------------------------------
# Prediction class distribution
# ---------------------------------------------------------

def calculate_class_distribution(
    predictions
):

    predictions = np.asarray(
        predictions
    )

    total = len(predictions)

    if total == 0:

        return {}

    unique, counts = np.unique(
        predictions,
        return_counts=True
    )

    distribution = {}

    for value, count in zip(
        unique,
        counts
    ):

        distribution[str(int(value))] = (
            float(count / total)
        )

    return distribution


# ---------------------------------------------------------
# Probability PSI
# ---------------------------------------------------------

def calculate_probability_psi(
    reference_probabilities,
    production_probabilities,
    bins=10
):

    # We monitor probability of class 1.
    #
    # Example:
    #
    # [0.12, 0.83, 0.42, 0.91]

    reference_scores = (
        reference_probabilities[:, 1]
    )

    production_scores = (
        production_probabilities[:, 1]
    )

    # Create common bins

    bin_edges = np.linspace(
        0,
        1,
        bins + 1
    )

    reference_counts, _ = np.histogram(
        reference_scores,
        bins=bin_edges
    )

    production_counts, _ = np.histogram(
        production_scores,
        bins=bin_edges
    )

    reference_distribution = (
        reference_counts
        / reference_counts.sum()
    )

    production_distribution = (
        production_counts
        / production_counts.sum()
    )

    psi = calculate_psi(
        reference_distribution,
        production_distribution
    )

    return {
        "psi": psi,
        "status": get_psi_status(psi),
    }


# ---------------------------------------------------------
# Probability KS test
# ---------------------------------------------------------

def calculate_probability_ks(
    reference_probabilities,
    production_probabilities
):

    reference_scores = (
        reference_probabilities[:, 1]
    )

    production_scores = (
        production_probabilities[:, 1]
    )

    statistic, p_value = ks_2samp(
        reference_scores,
        production_scores
    )

    if p_value < KS_P_VALUE_THRESHOLD:

        status = "DRIFT"

    else:

        status = "NORMAL"

    return {
        "statistic": float(
            statistic
        ),

        "p_value": float(
            p_value
        ),

        "status": status,
    }


# ---------------------------------------------------------
# Overall prediction drift
# ---------------------------------------------------------

def detect_prediction_drift(
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame
) -> Dict[str, Any]:

    # -----------------------------------------------------
    # Generate predictions
    # -----------------------------------------------------

    reference_predictions, reference_probabilities = (
        generate_predictions(
            reference_df
        )
    )

    production_predictions, production_probabilities = (
        generate_predictions(
            production_df
        )
    )

    # -----------------------------------------------------
    # Class distributions
    # -----------------------------------------------------

    reference_class_distribution = (
        calculate_class_distribution(
            reference_predictions
        )
    )

    production_class_distribution = (
        calculate_class_distribution(
            production_predictions
        )
    )

    # -----------------------------------------------------
    # Probability PSI
    # -----------------------------------------------------

    probability_psi = (
        calculate_probability_psi(
            reference_probabilities,
            production_probabilities
        )
    )

    # -----------------------------------------------------
    # Probability KS
    # -----------------------------------------------------

    probability_ks = (
        calculate_probability_ks(
            reference_probabilities,
            production_probabilities
        )
    )

    # -----------------------------------------------------
    # Overall status
    # -----------------------------------------------------

    if (
        probability_psi["status"]
        == "DRIFT"
        or
        probability_ks["status"]
        == "DRIFT"
    ):

        status = "DRIFT"

    elif (
        probability_psi["status"]
        == "WARNING"
    ):

        status = "WARNING"

    else:

        status = "NORMAL"

    return {

        "status": status,

        "class_distribution": {

            "reference":
                reference_class_distribution,

            "production":
                production_class_distribution,
        },

        "probability_drift": {

            "psi":
                probability_psi,

            "ks_test":
                probability_ks,
        },

    }