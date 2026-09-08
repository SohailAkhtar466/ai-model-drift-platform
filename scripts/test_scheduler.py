import time

from app.services.scheduler_service import (
    start_scheduler,
)


def main():

    print(
        "Starting scheduler..."
    )


    # Run every 1 minute for testing

    start_scheduler(
        interval_minutes=1
    )


    print(
        "Scheduler is running."
    )


    print(
        "Press CTRL+C to stop."
    )


    try:

        while True:

            time.sleep(1)


    except KeyboardInterrupt:

        print(
            "\nStopping scheduler..."
        )


if __name__ == "__main__":

    main()