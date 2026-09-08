from pathlib import Path
from typing import Dict, Any
import json

import pandas as pd

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.database.crud import (
    get_monitoring_runs,
    get_monitoring_run_by_id,
    get_alerts,
)

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Depends,
)

from app.schemas.monitoring import (
    MonitoringResponse,
)

from app.services.monitoring_service import (
    build_monitoring_report,
    save_monitoring_report,
)

from app.services.baseline_service import (
    load_reference_data,
)

from app.drift.data_drift import (
    detect_data_drift,
)

from app.drift.prediction_drift import (
    detect_prediction_drift,
)

from app.services.monitoring_history import (
    add_monitoring_run,
    get_recent_history,
)

from app.services.alert_service import (
    generate_alerts,
)

from app.services.database_monitoring_service import (
    save_report_to_database,
)

from app.services.scheduler_service import (
    get_scheduler_status,
    start_scheduler,
    stop_scheduler,
)


# ---------------------------------------------------------
# Router
# ---------------------------------------------------------

router = APIRouter()


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

BASELINE_PATH = (
    PROJECT_ROOT
    / "model"
    / "reference_baseline.json"
)

LATEST_REPORT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "latest_report.json"
)

REQUIRED_FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": (
            "AI Model Drift Detection Platform"
        ),
    }


# ---------------------------------------------------------
# Baseline endpoint
# ---------------------------------------------------------

@router.get("/baseline")
def get_baseline():

    if not BASELINE_PATH.exists():

        raise HTTPException(
            status_code=404,
            detail="Reference baseline not found."
        )

    try:

        with open(
            BASELINE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            baseline = json.load(file)

        return baseline

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ---------------------------------------------------------
# Validate production data
# ---------------------------------------------------------

def validate_production_data(
    df: pd.DataFrame
):
    """
    Validate uploaded production dataset.
    """

    # -----------------------------------------------------
    # Empty dataset
    # -----------------------------------------------------

    if df.empty:

        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV is empty."
        )


    # -----------------------------------------------------
    # Minimum rows
    # -----------------------------------------------------

    if len(df) < 50:

        raise HTTPException(
            status_code=400,
            detail=(
                "Production dataset must contain "
                "at least 50 rows."
            )
        )


    # -----------------------------------------------------
    # Missing columns
    # -----------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_FEATURES
        if column not in df.columns
    ]


    if missing_columns:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing required columns",
                "missing_columns": missing_columns,
            }
        )


    # -----------------------------------------------------
    # Numeric validation
    # -----------------------------------------------------

    for column in REQUIRED_FEATURES:

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):

            raise HTTPException(
                status_code=400,
                detail={
                    "error":
                        "Non-numeric feature detected",
                    "feature":
                        column,
                }
            )


    # -----------------------------------------------------
    # Infinite values
    # -----------------------------------------------------

    numeric_data = df[
        REQUIRED_FEATURES
    ]

    if numeric_data.isin(
        [float("inf"), float("-inf")]
    ).any().any():

        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset contains infinite "
                "values."
            )
        )


    return True


# ---------------------------------------------------------
# Monitor uploaded production data
# ---------------------------------------------------------

@router.post(
    "/monitor",
    response_model=MonitoringResponse
)
async def monitor_data(
    file: UploadFile = File(...)
) -> MonitoringResponse:

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )


    if not file.filename.lower().endswith(
        ".csv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )


    try:

        # -------------------------------------------------
        # Read uploaded CSV
        # -------------------------------------------------

        contents = await file.read()

        from io import BytesIO

        production_df = pd.read_csv(
            BytesIO(contents)
        )


        # -------------------------------------------------
        # Validate production data
        # -------------------------------------------------

        validate_production_data(
            production_df
        )


        # -------------------------------------------------
        # Load reference data
        # -------------------------------------------------

        reference_df = (
            load_reference_data()
        )


        # -------------------------------------------------
        # Run data drift detection
        # -------------------------------------------------

        drift_results = detect_data_drift(
            reference_df,
            production_df
        )


        # -------------------------------------------------
        # Build monitoring report
        # -------------------------------------------------

        report = build_monitoring_report(
            drift_results,
            reference_df,
            production_df
        )


        # -------------------------------------------------
        # Run prediction drift detection
        # -------------------------------------------------

        prediction_drift_result = (
            detect_prediction_drift(
                reference_df,
                production_df
            )
        )


        # -------------------------------------------------
        # Add prediction drift to report
        # -------------------------------------------------

        report[
            "prediction_drift"
        ] = prediction_drift_result


        # -------------------------------------------------
        # Update overall status
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Generate alerts
        # -------------------------------------------------

        alerts = generate_alerts(
            report
        )


        report[
            "alerts"
        ] = alerts

        # -------------------------------------------------
        # Save monitoring history JSON
        # -------------------------------------------------

        add_monitoring_run(
            report
        )

        # -------------------------------------------------
        # Save monitoring run to SQLite database
        # -------------------------------------------------

        save_report_to_database(
            report
        )

        # -------------------------------------------------
        # Save latest report JSON
        # -------------------------------------------------

        save_monitoring_report(
            report
        )


        # -------------------------------------------------
        # Return final report
        # -------------------------------------------------

        return report


    except HTTPException:

        raise


    except pd.errors.EmptyDataError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded CSV is empty "
                "or invalid."
            )
        )


    except pd.errors.ParserError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not parse uploaded CSV."
            )
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ---------------------------------------------------------
# Get monitoring history
# ---------------------------------------------------------

@router.get("/history")
def monitoring_history(
    limit: int = 50,
):

    if limit < 1:

        limit = 1


    if limit > 500:

        limit = 500


    return {
        "runs": get_recent_history(
            limit
        )
    }


# ---------------------------------------------------------
# Get latest saved report
# ---------------------------------------------------------

@router.get("/report")
def get_latest_report():

    if not LATEST_REPORT_PATH.exists():

        raise HTTPException(
            status_code=404,
            detail="No monitoring report available."
        )


    try:

        with open(
            LATEST_REPORT_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            report = json.load(file)

        return report


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

# ---------------------------------------------------------
# Scheduler status
# ---------------------------------------------------------

@router.get("/scheduler/status")
def scheduler_status():

    return get_scheduler_status()


# ---------------------------------------------------------
# Start scheduler
# ---------------------------------------------------------

@router.post("/scheduler/start")
def start_monitoring_scheduler(
    interval_minutes: int = 60,
):

    if interval_minutes < 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "Interval must be at least "
                "1 minute."
            )
        )


    start_scheduler(
        interval_minutes=interval_minutes
    )


    return {
        "message":
            "Monitoring scheduler started.",

        "interval_minutes":
            interval_minutes,
    }


# ---------------------------------------------------------
# Stop scheduler
# ---------------------------------------------------------

@router.post("/scheduler/stop")
def stop_monitoring_scheduler():

    stop_scheduler()

    return {
        "message":
            "Monitoring scheduler stopped."
    }

# ---------------------------------------------------------
# Get monitoring runs from database
# ---------------------------------------------------------

@router.get("/database/runs")
def get_database_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
):

    if limit < 1:

        limit = 1

    if limit > 500:

        limit = 500


    runs = get_monitoring_runs(
        db,
        limit,
    )


    return {
        "runs": [
            {
                "id": run.id,

                "timestamp": run.timestamp,

                "status": run.status,

                "total_features":
                    run.total_features,

                "drifted_features":
                    run.drifted_features,

                "warning_features":
                    run.warning_features,

                "healthy_features":
                    run.healthy_features,

                "reference_rows":
                    run.reference_rows,

                "production_rows":
                    run.production_rows,

                "prediction_drift":
                    run.prediction_drift,
            }

            for run in runs
        ]
    }

# ---------------------------------------------------------
# Get single monitoring run
# ---------------------------------------------------------

@router.get("/database/runs/{run_id}")
def get_database_run(
    run_id: int,
    db: Session = Depends(get_db),
):

    run = get_monitoring_run_by_id(
        db,
        run_id,
    )


    if not run:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Monitoring run "
                f"{run_id} not found."
            )
        )


    return {
        "id": run.id,

        "timestamp": run.timestamp,

        "status": run.status,

        "total_features":
            run.total_features,

        "drifted_features":
            run.drifted_features,

        "warning_features":
            run.warning_features,

        "healthy_features":
            run.healthy_features,

        "reference_rows":
            run.reference_rows,

        "production_rows":
            run.production_rows,

        "prediction_drift":
            run.prediction_drift,

        "alerts": [
            {
                "id": alert.id,

                "severity":
                    alert.severity,

                "type":
                    alert.type,

                "feature":
                    alert.feature,

                "message":
                    alert.message,

                "created_at":
                    alert.created_at,
            }

            for alert in run.alerts
        ],
    }

# ---------------------------------------------------------
# Get alerts from database
# ---------------------------------------------------------

@router.get("/database/alerts")
def get_database_alerts(
    limit: int = 100,
    db: Session = Depends(get_db),
):

    if limit < 1:

        limit = 1

    if limit > 500:

        limit = 500


    alerts = get_alerts(
        db,
        limit,
    )


    return {
        "alerts": [
            {
                "id": alert.id,

                "monitoring_run_id":
                    alert.monitoring_run_id,

                "severity":
                    alert.severity,

                "type":
                    alert.type,

                "feature":
                    alert.feature,

                "message":
                    alert.message,

                "created_at":
                    alert.created_at,
            }

            for alert in alerts
        ]
    }