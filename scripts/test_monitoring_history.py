from app.services.monitoring_history import (
    add_monitoring_run,
    get_recent_history,
)


def main():

    report = {

        "status": "HEALTHY",

        "summary": {

            "total_features": 5,

            "drifted_features": 0,

            "warning_features": 1,

            "healthy_features": 4,
        },

        "dataset": {

            "reference_rows": 5000,

            "production_rows": 1000,
        },

        "prediction_drift": {

            "status": "NORMAL",
        },
    }


    print(
        "Saving test monitoring run..."
    )


    run = add_monitoring_run(
        report
    )


    print(
        "\nSaved Run:"
    )

    print(run)


    print(
        "\nMonitoring History:"
    )


    history = get_recent_history()

    for item in history:

        print(item)


if __name__ == "__main__":

    main()