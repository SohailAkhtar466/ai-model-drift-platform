from typing import Dict, Any

from app.database.database import (
    SessionLocal,
)

from app.database.crud import (
    save_monitoring_report_to_db,
)


# =========================================================
# Save Report to Database
# =========================================================

def save_report_to_database(
    report: Dict[str, Any],
):

    db = SessionLocal()

    try:

        monitoring_run = (
            save_monitoring_report_to_db(
                db,
                report,
            )
        )

        return monitoring_run

    finally:

        db.close()