from app.services.automated_monitoring_service import (
    run_automated_monitoring,
)


def main():

    print(
        "\nStarting automated monitoring..."
    )


    report = (
        run_automated_monitoring()
    )


    print(
        "\nMonitoring completed."
    )


    print(
        f"\nStatus: "
        f"{report.get('status')}"
    )


    print(
        f"Drifted Features: "
        f"{report.get('summary', {}).get('drifted_features')}"
    )


    print(
        f"Alerts: "
        f"{len(report.get('alerts', []))}"
    )


if __name__ == "__main__":

    main()