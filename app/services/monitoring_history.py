from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone

import json


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


REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
)


HISTORY_PATH = (
    REPORTS_DIR
    / "history.json"
)


# =========================================================
# Ensure reports directory exists
# =========================================================

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# Load history
# =========================================================

def load_history() -> List[Dict[str, Any]]:

    if not HISTORY_PATH.exists():

        return []

    try:

        with open(
            HISTORY_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            list,
        ):

            return []

        return data

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


# =========================================================
# Save history
# =========================================================

def save_history(
    history: List[Dict[str, Any]]
) -> None:

    with open(
        HISTORY_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            history,
            file,
            indent=4,
        )


# =========================================================
# Add monitoring run
# =========================================================

def add_monitoring_run(
    report: Dict[str, Any],
) -> Dict[str, Any]:

    history = load_history()

    summary = report.get(
        "summary",
        {},
    )

    prediction_drift = report.get(
        "prediction_drift",
        {},
    )

    run = {

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "status": report.get(
            "status",
            "UNKNOWN",
        ),

        "total_features": summary.get(
            "total_features",
            0,
        ),

        "drifted_features": summary.get(
            "drifted_features",
            0,
        ),

        "warning_features": summary.get(
            "warning_features",
            0,
        ),

        "healthy_features": summary.get(
            "healthy_features",
            0,
        ),

        "reference_rows": report.get(
            "dataset",
            {},
        ).get(
            "reference_rows",
            0,
        ),

        "production_rows": report.get(
            "dataset",
            {},
        ).get(
            "production_rows",
            0,
        ),

        "prediction_drift": prediction_drift.get(
            "status",
            "UNKNOWN",
        ),
    }


    history.append(
        run
    )


    save_history(
        history
    )


    return run


# =========================================================
# Get recent history
# =========================================================

def get_recent_history(
    limit: int = 50,
) -> List[Dict[str, Any]]:

    history = load_history()

    return history[
        -limit:
    ]


# =========================================================
# Clear history
# =========================================================

def clear_history() -> None:

    save_history([])