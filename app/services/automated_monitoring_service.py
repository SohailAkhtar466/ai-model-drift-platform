from pathlib import Path
from typing import Dict, Any

import pandas as pd

from app.services.baseline_service import (
    load_reference_data,
)

from app.services.monitoring_service import (
    build_monitoring_report,
    save_monitoring_report,
)

from app.services.monitoring_history import (
    add_monitoring_run,
)

from app.services.alert_service import (
    generate_alerts,
)

from app.drift.data_drift import (
    detect_data_drift,
)

from app.drift.prediction_drift import (
    detect_prediction_drift,
)

from app.services.database_monitoring_service import (
    save_report_to_database,
)


# =========================================================
# Project paths
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


PRODUCTION_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "production"
    / "production.csv"
)


# =========================================================
# Run automated monitoring
# =========================================================

def run_automated_monitoring() -> Dict[str, Any]:
    """
    Run complete monitoring automatically
    using the production.csv file.
    """

    # -----------------------------------------------------
    # Check production file
    # -----------------------------------------------------

    if not PRODUCTION_DATA_PATH.exists():

        raise FileNotFoundError(
            "Production dataset not found: "
            f"{PRODUCTION_DATA_PATH}"
        )


    # -----------------------------------------------------
    # Load production data
    # -----------------------------------------------------

    production_df = pd.read_csv(
        PRODUCTION_DATA_PATH
    )


    if production_df.empty:

        raise ValueError(
            "Production dataset is empty."
        )


    # -----------------------------------------------------
    # Load reference data
    # -----------------------------------------------------

    reference_df = (
        load_reference_data()
    )


    # -----------------------------------------------------
    # Data drift detection
    # -----------------------------------------------------

    drift_results = (
        detect_data_drift(
            reference_df,
            production_df
        )
    )


    # -----------------------------------------------------
    # Build monitoring report
    # -----------------------------------------------------

    report = (
        build_monitoring_report(
            drift_results,
            reference_df,
            production_df
        )
    )


    # -----------------------------------------------------
    # Prediction drift
    # -----------------------------------------------------

    prediction_drift_result = (
        detect_prediction_drift(
            reference_df,
            production_df
        )
    )


    report[
        "prediction_drift"
    ] = prediction_drift_result


    # -----------------------------------------------------
    # Update overall status
    # -----------------------------------------------------

    prediction_status = (
        prediction_drift_result.get(
            "status",
            "UNKNOWN"
        )
    )


    if prediction_status == "DRIFT":

        report[
            "status"
        ] = "DRIFT_DETECTED"


    elif (
        prediction_status == "WARNING"
        and
        report.get("status")
        == "HEALTHY"
    ):

        report[
            "status"
        ] = "WARNING"


    # -----------------------------------------------------
    # Generate alerts
    # -----------------------------------------------------

    alerts = generate_alerts(
        report
    )


    report[
        "alerts"
    ] = alerts

    # -----------------------------------------------------
    # Save history
    # -----------------------------------------------------

    add_monitoring_run(
        report
    )

    # -----------------------------------------------------
    # Save latest report
    # -----------------------------------------------------

    save_monitoring_report(
        report
    )


    return report