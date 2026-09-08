import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd

from app.drift.data_drift import detect_data_drift
from app.drift.prediction_drift import (
    detect_prediction_drift,
)


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

PRODUCTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "production.csv"
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
# Load reference data
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
# Load production data
# ---------------------------------------------------------

def load_production_data() -> pd.DataFrame:

    if not PRODUCTION_PATH.exists():

        raise FileNotFoundError(
            f"Production dataset not found:\n"
            f"{PRODUCTION_PATH}"
        )

    return pd.read_csv(
        PRODUCTION_PATH
    )


# ---------------------------------------------------------
# Determine feature status
# ---------------------------------------------------------

def determine_feature_status(
    result: Dict[str, Any]
) -> str:

    psi_status = result["psi_status"]

    ks_status = result["ks_test"]["status"]

    # If either statistical test detects drift,
    # consider the feature drifted.

    if (
        psi_status == "DRIFT"
        or ks_status == "DRIFT"
    ):

        return "DRIFT"

    # If either test gives a warning,
    # consider the feature in warning state.

    if (
        psi_status == "WARNING"
    ):

        return "WARNING"

    return "NORMAL"


# ---------------------------------------------------------
# Build monitoring report
# ---------------------------------------------------------

def build_monitoring_report(
    drift_results: Dict[str, Any],
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame
) -> Dict[str, Any]:

    feature_results = {}

    drifted_features = []
    warning_features = []

    # -----------------------------------------------------
    # Analyze every feature
    # -----------------------------------------------------

    for feature, result in drift_results.items():

        status = determine_feature_status(
            result
        )

        feature_results[feature] = {
            "status": status,

            "psi": result["psi"],

            "psi_status": result[
                "psi_status"
            ],

            "ks_test": result[
                "ks_test"
            ],

            "missing_values": result[
                "missing_values"
            ],
        }

        if status == "DRIFT":

            drifted_features.append(
                feature
            )

        elif status == "WARNING":

            warning_features.append(
                feature
            )

    # -----------------------------------------------------
    # Overall status
    # -----------------------------------------------------

    if len(drifted_features) > 0:

        overall_status = "DRIFT_DETECTED"

    elif len(warning_features) > 0:

        overall_status = "WARNING"

    else:

        overall_status = "HEALTHY"

    # -----------------------------------------------------
    # Build report
    # -----------------------------------------------------

    report = {

        "status": overall_status,

        "dataset": {

            "reference_rows": int(
                len(reference_df)
            ),

            "production_rows": int(
                len(production_df)
            ),

            "features_monitored": len(
                FEATURES
            ),
        },

        "summary": {

            "total_features": len(
                FEATURES
            ),

            "drifted_features": len(
                drifted_features
            ),

            "warning_features": len(
                warning_features
            ),

            "healthy_features": (
                len(FEATURES)
                - len(drifted_features)
                - len(warning_features)
            ),
        },

        "drifted_feature_names":
            drifted_features,

        "warning_feature_names":
            warning_features,

        "features":
            feature_results,
    }

    return report


# ---------------------------------------------------------
# Complete monitoring pipeline
# ---------------------------------------------------------

def run_monitoring() -> Dict[str, Any]:

    print(
        "Loading reference dataset..."
    )

    reference_df = (
        load_reference_data()
    )

    print(
        "Loading production dataset..."
    )

    production_df = (
        load_production_data()
    )

    # -----------------------------------------------------
    # Data drift
    # -----------------------------------------------------

    print(
        "Running data drift detection..."
    )

    data_drift_results = (
        detect_data_drift(
            reference_df,
            production_df
        )
    )

    # -----------------------------------------------------
    # Prediction drift
    # -----------------------------------------------------

    print(
        "Running prediction drift detection..."
    )

    prediction_drift_result = (
        detect_prediction_drift(
            reference_df,
            production_df
        )
    )

    # -----------------------------------------------------
    # Build report
    # -----------------------------------------------------

    print(
        "Building monitoring report..."
    )

    report = build_monitoring_report(
        data_drift_results,
        reference_df,
        production_df
    )

    # -----------------------------------------------------
    # Add prediction drift
    # -----------------------------------------------------

    report[
        "prediction_drift"
    ] = prediction_drift_result

    # -----------------------------------------------------
    # Update overall status
    # -----------------------------------------------------

    if (
        prediction_drift_result["status"]
        == "DRIFT"
    ):

        report[
            "status"
        ] = "DRIFT_DETECTED"

    elif (
        prediction_drift_result["status"]
        == "WARNING"
        and
        report["status"]
        == "HEALTHY"
    ):

        report[
            "status"
        ] = "WARNING"

    return report


# ---------------------------------------------------------
# Display report
# ---------------------------------------------------------

def print_monitoring_report(
    report: Dict[str, Any]
):

    print("\n")
    print("=" * 70)
    print("AI MODEL MONITORING REPORT")
    print("=" * 70)

    print(
        f"\nOverall Status: "
        f"{report['status']}"
    )

    print(
        f"\nTotal Features: "
        f"{report['summary']['total_features']}"
    )

    print(
        f"Drifted Features: "
        f"{report['summary']['drifted_features']}"
    )

    print(
        f"Warning Features: "
        f"{report['summary']['warning_features']}"
    )

    print(
        f"Healthy Features: "
        f"{report['summary']['healthy_features']}"
    )

    print("\n")
    print("-" * 70)
    print("FEATURE DETAILS")
    print("-" * 70)

    for feature, result in (
        report["features"].items()
    ):

        print(
            f"\n{feature}"
        )

        print(
            f"  Status: "
            f"{result['status']}"
        )

        print(
            f"  PSI: "
            f"{result['psi']:.4f}"
        )

        print(
            f"  PSI Status: "
            f"{result['psi_status']}"
        )

        print(
            f"  KS Statistic: "
            f"{result['ks_test']['statistic']:.4f}"
        )

        print(
            f"  KS P-Value: "
            f"{result['ks_test']['p_value']:.4f}"
        )

        print(
            f"  KS Status: "
            f"{result['ks_test']['status']}"
        )

    print("\n")
    print("=" * 70)





# ---------------------------------------------------------
# Save monitoring report
# ---------------------------------------------------------

def save_monitoring_report(
    report: Dict[str, Any]
):

    reports_dir = (
        PROJECT_ROOT
        / "reports"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path = (
        reports_dir
        / "latest_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"\nMonitoring report saved to:\n"
        f"{report_path}"
    )

# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":

    report = run_monitoring()

    print_monitoring_report(
        report
    )

    save_monitoring_report(
        report
    )