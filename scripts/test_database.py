from app.database.database import (
    SessionLocal,
)

from app.database.crud import (
    save_monitoring_report_to_db,
    get_monitoring_runs,
    get_alerts,
)


def main():

    db = SessionLocal()


    try:

        # -------------------------------------------------
        # Test Report
        # -------------------------------------------------

        report = {

            "status": "DRIFT_DETECTED",

            "summary": {

                "total_features": 5,

                "drifted_features": 2,

                "warning_features": 1,

                "healthy_features": 2,
            },

            "dataset": {

                "reference_rows": 5000,

                "production_rows": 1000,
            },

            "prediction_drift": {

                "status": "DRIFT",
            },

            "alerts": [

                {
                    "severity": "CRITICAL",

                    "type": "MODEL_DRIFT",

                    "message": (
                        "Significant model drift "
                        "has been detected."
                    ),
                },

                {
                    "severity": "CRITICAL",

                    "type": "FEATURE_DRIFT",

                    "feature": "age",

                    "message": (
                        "Drift detected in "
                        "feature 'age'."
                    ),
                },

            ],
        }


        # -------------------------------------------------
        # Save Report
        # -------------------------------------------------

        monitoring_run = (
            save_monitoring_report_to_db(
                db,
                report,
            )
        )


        print(
            "\nMonitoring Run Saved:"
        )

        print(
            f"ID: {monitoring_run.id}"
        )

        print(
            f"Status: {monitoring_run.status}"
        )


        # -------------------------------------------------
        # Get Runs
        # -------------------------------------------------

        runs = get_monitoring_runs(
            db
        )


        print(
            "\nMonitoring Runs:"
        )


        for run in runs:

            print(
                f"ID={run.id} | "
                f"Status={run.status} | "
                f"Drifted={run.drifted_features}"
            )


        # -------------------------------------------------
        # Get Alerts
        # -------------------------------------------------

        alerts = get_alerts(
            db
        )


        print(
            "\nAlerts:"
        )


        for alert in alerts:

            print(
                f"ID={alert.id} | "
                f"Severity={alert.severity} | "
                f"Type={alert.type} | "
                f"Message={alert.message}"
            )


    finally:

        db.close()


if __name__ == "__main__":

    main()