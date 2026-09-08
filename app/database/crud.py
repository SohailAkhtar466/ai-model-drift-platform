from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.database.models import (
    MonitoringRun,
    Alert,
)


# =========================================================
# Create Monitoring Run
# =========================================================

def create_monitoring_run(
    db: Session,
    report: Dict[str, Any],
) -> MonitoringRun:

    summary = report.get(
        "summary",
        {},
    )

    dataset = report.get(
        "dataset",
        {},
    )

    prediction_drift = report.get(
        "prediction_drift",
        {},
    )

    monitoring_run = MonitoringRun(

        status=report.get(
            "status",
            "UNKNOWN",
        ),

        total_features=summary.get(
            "total_features",
            0,
        ),

        drifted_features=summary.get(
            "drifted_features",
            0,
        ),

        warning_features=summary.get(
            "warning_features",
            0,
        ),

        healthy_features=summary.get(
            "healthy_features",
            0,
        ),

        reference_rows=dataset.get(
            "reference_rows",
            0,
        ),

        production_rows=dataset.get(
            "production_rows",
            0,
        ),

        prediction_drift=prediction_drift.get(
            "status",
            "UNKNOWN",
        ),
    )

    db.add(
        monitoring_run
    )

    db.commit()

    db.refresh(
        monitoring_run
    )

    return monitoring_run


# =========================================================
# Create Alerts
# =========================================================

def create_alerts(
    db: Session,
    monitoring_run_id: int,
    alerts: List[Dict[str, Any]],
) -> List[Alert]:

    created_alerts = []

    for alert_data in alerts:

        alert = Alert(

            monitoring_run_id=(
                monitoring_run_id
            ),

            severity=alert_data.get(
                "severity",
                "INFO",
            ),

            type=alert_data.get(
                "type",
                "UNKNOWN",
            ),

            feature=alert_data.get(
                "feature",
            ),

            message=alert_data.get(
                "message",
                "",
            ),
        )

        db.add(
            alert
        )

        created_alerts.append(
            alert
        )


    db.commit()


    for alert in created_alerts:

        db.refresh(
            alert
        )


    return created_alerts


# =========================================================
# Save Complete Monitoring Report
# =========================================================

def save_monitoring_report_to_db(
    db: Session,
    report: Dict[str, Any],
) -> MonitoringRun:

    # -----------------------------------------------------
    # Save monitoring run
    # -----------------------------------------------------

    monitoring_run = (
        create_monitoring_run(
            db,
            report,
        )
    )


    # -----------------------------------------------------
    # Save alerts
    # -----------------------------------------------------

    alerts = report.get(
        "alerts",
        [],
    )


    if alerts:

        create_alerts(
            db,
            monitoring_run.id,
            alerts,
        )


    return monitoring_run


# =========================================================
# Get Monitoring Runs
# =========================================================

def get_monitoring_runs(
    db: Session,
    limit: int = 50,
):

    return (
        db.query(
            MonitoringRun
        )
        .order_by(
            MonitoringRun.timestamp.desc()
        )
        .limit(
            limit
        )
        .all()
    )


# =========================================================
# Get Monitoring Run By ID
# =========================================================

def get_monitoring_run_by_id(
    db: Session,
    run_id: int,
):

    return (
        db.query(
            MonitoringRun
        )
        .filter(
            MonitoringRun.id == run_id
        )
        .first()
    )


# =========================================================
# Get Alerts
# =========================================================

def get_alerts(
    db: Session,
    limit: int = 100,
):

    return (
        db.query(
            Alert
        )
        .order_by(
            Alert.created_at.desc()
        )
        .limit(
            limit
        )
        .all()
    )