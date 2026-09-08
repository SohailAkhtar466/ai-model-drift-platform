
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

RANDOM_STATE = 42

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

REFERENCE_DIR = DATA_DIR / "reference"
PRODUCTION_DIR = DATA_DIR / "production"

MODEL_DIR = PROJECT_ROOT / "model"

REFERENCE_PATH = REFERENCE_DIR / "reference.csv"
PRODUCTION_PATH = PRODUCTION_DIR / "production.csv"

MODEL_PATH = MODEL_DIR / "churn_model.joblib"


FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]

TARGET = "churn"


# ---------------------------------------------------------
# Create synthetic customer data
# ---------------------------------------------------------

def create_customer_data(n_samples=5000, random_state=42):

    rng = np.random.default_rng(random_state)

    age = rng.integers(
        low=18,
        high=70,
        size=n_samples
    )

    monthly_income = rng.normal(
        loc=60000,
        scale=20000,
        size=n_samples
    )

    monthly_income = np.clip(
        monthly_income,
        15000,
        150000
    )

    account_balance = rng.normal(
        loc=120000,
        scale=60000,
        size=n_samples
    )

    account_balance = np.clip(
        account_balance,
        5000,
        500000
    )

    login_frequency = rng.poisson(
        lam=12,
        size=n_samples
    )

    support_tickets = rng.poisson(
        lam=2,
        size=n_samples
    )

    # -----------------------------------------------------
    # Create churn probability
    # -----------------------------------------------------

    churn_score = (
        -0.04 * login_frequency
        + 0.30 * support_tickets
        - 0.000003 * account_balance
        - 0.000002 * monthly_income
        + 0.01 * age
    )

    churn_probability = 1 / (
        1 + np.exp(-churn_score)
    )

    churn = rng.binomial(
        1,
        churn_probability
    )

    df = pd.DataFrame({
        "age": age,
        "monthly_income": monthly_income.round(2),
        "account_balance": account_balance.round(2),
        "login_frequency": login_frequency,
        "support_tickets": support_tickets,
        "churn": churn,
    })

    return df


# ---------------------------------------------------------
# Train model
# ---------------------------------------------------------

def train_model():

    print("Creating dataset...")

    df = create_customer_data(
        n_samples=5000,
        random_state=RANDOM_STATE
    )

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print("Training model...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # Evaluation
    # -----------------------------------------------------

    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print("\nModel Accuracy:")
    print(round(accuracy, 4))

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions
        )
    )

    # -----------------------------------------------------
    # Create directories
    # -----------------------------------------------------

    REFERENCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    PRODUCTION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save reference dataset
    # -----------------------------------------------------

    df.to_csv(
        REFERENCE_PATH,
        index=False
    )

    print(
        f"\nReference dataset saved to: "
        f"{REFERENCE_PATH}"
    )

    # -----------------------------------------------------
    # Save model
    # -----------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"Model saved to: "
        f"{MODEL_PATH}"
    )

    return model, df


# ---------------------------------------------------------
# Generate production data
# ---------------------------------------------------------

def create_production_data(
    n_samples=2000,
    random_state=100
):

    production_df = create_customer_data(
        n_samples=n_samples,
        random_state=random_state
    )

    # -----------------------------------------------------
    # Simulate production distribution shift
    # -----------------------------------------------------

    production_df["monthly_income"] = (
        production_df["monthly_income"] * 1.8
    )

    production_df["age"] = (
        production_df["age"] + 8
    )

    production_df["support_tickets"] = (
        production_df["support_tickets"] + 2
    )

    # Keep values within realistic ranges

    production_df["monthly_income"] = (
        production_df["monthly_income"]
        .clip(15000, 200000)
    )

    production_df["age"] = (
        production_df["age"]
        .clip(18, 70)
    )

    production_df.to_csv(
        PRODUCTION_PATH,
        index=False
    )

    print(
        f"Production dataset saved to: "
        f"{PRODUCTION_PATH}"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    train_model()

    create_production_data()

    print("\nTraining pipeline completed successfully.")