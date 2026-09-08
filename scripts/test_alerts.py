from app.services.alert_service import (
    generate_alerts,
)


def main():

    report = {

        "status": "DRIFT_DETECTED",

        "summary": {

            "total_features": 5,

            "drifted_features": 2,

            "warning_features": 1,

            "healthy_features": 2,
        },

        "drifted_feature_names": [
            "age",
            "monthly_income",
        ],

        "warning_feature_names": [
            "account_balance",
        ],

        "prediction_drift": {

            "status": "DRIFT",
        },
    }


    alerts = generate_alerts(
        report
    )


    print(
        "\nGenerated Alerts:"
    )


    for alert in alerts:

        print(
            f"\n[{alert['severity']}] "
            f"{alert['type']}"
        )

        print(
            alert["message"]
        )


if __name__ == "__main__":

    main()