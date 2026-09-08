from apscheduler.schedulers.background import (
    BackgroundScheduler,
)

from app.services.automated_monitoring_service import (
    run_automated_monitoring,
)


# =========================================================
# Scheduler
# =========================================================

scheduler = BackgroundScheduler()


# =========================================================
# Monitoring job
# =========================================================

def monitoring_job():

    print(
        "\n[Scheduler] Starting automated monitoring..."
    )

    try:

        report = (
            run_automated_monitoring()
        )

        print(
            "[Scheduler] Monitoring completed."
        )

        print(
            f"[Scheduler] Status: "
            f"{report.get('status')}"
        )

    except Exception as error:

        print(
            f"[Scheduler] Monitoring failed: "
            f"{error}"
        )


# =========================================================
# Start scheduler
# =========================================================

def start_scheduler(
    interval_minutes: int = 60,
):

    # Remove existing job if present

    existing_job = scheduler.get_job(
        "automated_monitoring"
    )

    if existing_job:

        scheduler.remove_job(
            "automated_monitoring"
        )


    # Add new monitoring job

    scheduler.add_job(

        monitoring_job,

        trigger="interval",

        minutes=interval_minutes,

        id="automated_monitoring",

        replace_existing=True,

    )


    # Start scheduler only if not already running

    if not scheduler.running:

        scheduler.start()


    print(
        f"Automated monitoring scheduler configured. "
        f"Interval: {interval_minutes} minutes."
    )


# =========================================================
# Stop scheduler
# =========================================================

def stop_scheduler():

    if scheduler.running:

        scheduler.shutdown()

        print(
            "Automated monitoring scheduler stopped."
        )


# =========================================================
# Get scheduler status
# =========================================================

def get_scheduler_status():

    return {

        "running":
            scheduler.running,

        "jobs":
            [
                {
                    "id": job.id,

                    "next_run_time":
                        (
                            str(
                                job.next_run_time
                            )
                            if job.next_run_time
                            else None
                        ),
                }

                for job in scheduler.get_jobs()
            ],
    }