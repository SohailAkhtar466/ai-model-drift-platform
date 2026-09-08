from typing import Any, Dict, List


# =========================================================
# Alert severity
# =========================================================

INFO = "INFO"
WARNING = "WARNING"
CRITICAL = "CRITICAL"


# =========================================================
# Create monitoring alerts
# =========================================================

def generate_alerts(
    report: Dict[str, Any],
) -> List[Dict[str, Any]]:

    alerts = []


    status = report.get(
        "status",
        "UNKNOWN",
    )


    summary = report.get(
        "summary",
        {},
    )


    # -----------------------------------------------------
    # Critical overall drift
    # -----------------------------------------------------

    if status == "DRIFT_DETECTED":

        alerts.append(
            {
                "severity": CRITICAL,

                "type": "MODEL_DRIFT",

                "message": (
                    "Significant model drift "
                    "has been detected."
                ),
            }
        )


    # -----------------------------------------------------
    # Warning
    # -----------------------------------------------------

    elif status == "WARNING":

        alerts.append(
            {
                "severity": WARNING,

                "type": "MODEL_WARNING",

                "message": (
                    "Potential model drift "
                    "requires investigation."
                ),
            }
        )


    # -----------------------------------------------------
    # Feature-specific alerts
    # -----------------------------------------------------

    drifted_features = report.get(
        "drifted_feature_names",
        [],
    )


    warning_features = report.get(
        "warning_feature_names",
        [],
    )


    for feature in drifted_features:

        alerts.append(
            {
                "severity": CRITICAL,

                "type": "FEATURE_DRIFT",

                "feature": feature,

                "message": (
                    f"Drift detected in "
                    f"feature '{feature}'."
                ),
            }
        )


    for feature in warning_features:

        alerts.append(
            {
                "severity": WARNING,

                "type": "FEATURE_WARNING",

                "feature": feature,

                "message": (
                    f"Potential drift detected "
                    f"in feature '{feature}'."
                ),
            }
        )


    # -----------------------------------------------------
    # Prediction drift
    # -----------------------------------------------------

    prediction_drift = report.get(
        "prediction_drift",
        {},
    )


    prediction_status = (
        prediction_drift.get(
            "status",
            "UNKNOWN",
        )
    )


    if prediction_status == "DRIFT":

        alerts.append(
            {
                "severity": CRITICAL,

                "type": "PREDICTION_DRIFT",

                "message": (
                    "Model prediction distribution "
                    "has changed significantly."
                ),
            }
        )


    elif prediction_status == "WARNING":

        alerts.append(
            {
                "severity": WARNING,

                "type": "PREDICTION_WARNING",

                "message": (
                    "Model prediction distribution "
                    "may be changing."
                ),
            }
        )


    return alerts