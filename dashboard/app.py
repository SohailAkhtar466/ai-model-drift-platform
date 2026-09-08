from pathlib import Path
import io
import json

import pandas as pd
import requests
import streamlit as st
import matplotlib.pyplot as plt


# =========================================================
# Configuration
# =========================================================

API_URL = "http://127.0.0.1:8000"

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

REFERENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "reference.csv"
)

FEATURES = [
    "age",
    "monthly_income",
    "account_balance",
    "login_frequency",
    "support_tickets",
]


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="AI Model Monitoring",
    page_icon="🤖",
    layout="wide",
)


# =========================================================
# Custom CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
    }

    .subtitle {
        color: #6b7280;
        font-size: 16px;
    }

    .status-box {
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 20px;
        font-size: 22px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Header
# =========================================================

st.markdown(
    '<div class="main-title">'
    '🤖 AI Model Drift Monitoring Platform'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Monitor production data and model behavior '
    'for distribution changes.'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# Load Reference Dataset
# =========================================================

@st.cache_data
def load_reference_data():

    return pd.read_csv(
        REFERENCE_PATH
    )


try:

    reference_df = load_reference_data()

except Exception as error:

    st.error(
        f"Could not load reference dataset: {error}"
    )

    st.stop()


# =========================================================
# API Health
# =========================================================

def check_api():

    try:

        response = requests.get(
            f"{API_URL}/health",
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:

        return False


api_online = check_api()


# =========================================================
# Sidebar
# =========================================================

st.sidebar.title(
    "⚙️ Monitoring"
)

if api_online:

    st.sidebar.success(
        "🟢 API Online"
    )

else:

    st.sidebar.error(
        "🔴 API Offline"
    )


st.sidebar.divider()

st.sidebar.subheader(
    "Production Dataset"
)

uploaded_file = st.sidebar.file_uploader(
    "Upload production CSV",
    type=["csv"],
)


# =========================================================
# Run Monitoring
# =========================================================

if uploaded_file is not None:

    if st.sidebar.button(
        "🔍 Run Drift Detection",
        use_container_width=True,
    ):

        if not api_online:

            st.error(
                "FastAPI is offline. "
                "Start the API first."
            )

        else:

            with st.spinner(
                "Running model monitoring..."
            ):

                try:

                    file_bytes = (
                        uploaded_file.getvalue()
                    )

                    files = {
                        "file": (
                            uploaded_file.name,
                            file_bytes,
                            "text/csv",
                        )
                    }

                    response = requests.post(
                        f"{API_URL}/monitor",
                        files=files,
                        timeout=120,
                    )

                    if response.status_code == 200:

                        st.session_state[
                            "report"
                        ] = response.json()

                        st.session_state[
                            "production_df"
                        ] = pd.read_csv(
                            io.BytesIO(
                                file_bytes
                            )
                        )

                        st.session_state[
                            "uploaded_file_name"
                        ] = uploaded_file.name

                        st.success(
                            "Monitoring completed successfully."
                        )

                    else:

                        try:

                            error_data = (
                                response.json()
                            )

                            st.error(
                                error_data
                            )

                        except Exception:

                            st.error(
                                response.text
                            )

                except requests.RequestException as error:

                    st.error(
                        f"API connection error: {error}"
                    )


# =========================================================
# Retrieve Session Data
# =========================================================

report = st.session_state.get(
    "report"
)

production_df = st.session_state.get(
    "production_df"
)


# =========================================================
# Empty State
# =========================================================

if report is None:

    st.info(
        "👈 Upload a production CSV from the "
        "sidebar and click **Run Drift Detection**."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Reference Rows",
            len(reference_df),
        )

    with col2:

        st.metric(
            "Features",
            len(FEATURES),
        )

    with col3:

        st.metric(
            "Monitoring Engine",
            "PSI + KS",
        )

    st.subheader(
        "Reference Dataset Preview"
    )

    st.dataframe(
        reference_df.head(10),
        use_container_width=True,
        hide_index=True,
    )

    st.stop()


# =========================================================
# Status
# =========================================================

status = report.get(
    "status",
    "UNKNOWN",
)


if status == "DRIFT_DETECTED":

    st.error(
        "🚨 MODEL DATA HEALTH: DRIFT DETECTED"
    )

elif status == "WARNING":

    st.warning(
        "⚠️ MODEL DATA HEALTH: WARNING"
    )

elif status == "HEALTHY":

    st.success(
        "✅ MODEL DATA HEALTH: HEALTHY"
    )

else:

    st.info(
        f"Model status: {status}"
    )


# =========================================================
# Summary
# =========================================================

summary = report.get(
    "summary",
    {},
)

dataset = report.get(
    "dataset",
    {},
)


st.subheader(
    "📊 Monitoring Overview"
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Features",
        summary.get(
            "total_features",
            0,
        ),
    )


with col2:

    st.metric(
        "🚨 Drifted",
        summary.get(
            "drifted_features",
            0,
        ),
    )


with col3:

    st.metric(
        "⚠️ Warnings",
        summary.get(
            "warning_features",
            0,
        ),
    )


with col4:

    st.metric(
        "✅ Healthy",
        summary.get(
            "healthy_features",
            0,
        ),
    )


with col5:

    st.metric(
        "Production Rows",
        dataset.get(
            "production_rows",
            0,
        ),
    )


# =========================================================
# Dataset Information
# =========================================================

st.subheader(
    "📁 Dataset Information"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Reference Rows",
        dataset.get(
            "reference_rows",
            0,
        ),
    )


with col2:

    st.metric(
        "Production Rows",
        dataset.get(
            "production_rows",
            0,
        ),
    )


with col3:

    st.metric(
        "Features Monitored",
        dataset.get(
            "features_monitored",
            0,
        ),
    )


# =========================================================
# Feature Drift Table
# =========================================================

st.subheader(
    "🔎 Feature Drift Analysis"
)


features_result = report.get(
    "features",
    {},
)


rows = []


for feature, result in features_result.items():

    rows.append(
        {
            "Feature": feature,
            "Status": result.get(
                "status",
                "UNKNOWN",
            ),
            "PSI": result.get(
                "psi",
                0,
            ),
            "PSI Status": result.get(
                "psi_status",
                "UNKNOWN",
            ),
            "KS Statistic": result.get(
                "ks_test",
                {},
            ).get(
                "statistic",
                0,
            ),
            "KS P-Value": result.get(
                "ks_test",
                {},
            ).get(
                "p_value",
                0,
            ),
            "KS Status": result.get(
                "ks_test",
                {},
            ).get(
                "status",
                "UNKNOWN",
            ),
        }
    )


results_df = pd.DataFrame(
    rows
)


if not results_df.empty:

    display_df = results_df.copy()

    display_df["PSI"] = (
        display_df["PSI"].round(4)
    )

    display_df["KS Statistic"] = (
        display_df[
            "KS Statistic"
        ].round(4)
    )

    display_df["KS P-Value"] = (
        display_df[
            "KS P-Value"
        ].round(4)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# PSI Chart
# =========================================================

st.subheader(
    "📈 Population Stability Index"
)


if not results_df.empty:

    fig, ax = plt.subplots()

    ax.bar(
        results_df["Feature"],
        results_df["PSI"],
    )

    ax.axhline(
        0.10,
        linestyle="--",
        label="Warning threshold (0.10)",
    )

    ax.axhline(
        0.20,
        linestyle="--",
        label="Drift threshold (0.20)",
    )

    ax.set_ylabel(
        "PSI"
    )

    ax.set_xlabel(
        "Feature"
    )

    ax.set_title(
        "PSI by Feature"
    )

    ax.tick_params(
        axis="x",
        rotation=30,
    )

    ax.legend()

    st.pyplot(
        fig
    )

    plt.close(
        fig
    )


# =========================================================
# Feature Distribution
# =========================================================

st.subheader(
    "📊 Reference vs Production Distribution"
)


if production_df is not None:

    available_features = [
        feature
        for feature in FEATURES
        if (
            feature in reference_df.columns
            and
            feature in production_df.columns
        )
    ]

    selected_feature = st.selectbox(
        "Select a feature",
        available_features,
    )


    reference_values = (
        reference_df[
            selected_feature
        ]
        .dropna()
        .values
    )

    production_values = (
        production_df[
            selected_feature
        ]
        .dropna()
        .values
    )


    fig, ax = plt.subplots()

    ax.hist(
        reference_values,
        bins=30,
        alpha=0.55,
        label="Reference",
    )

    ax.hist(
        production_values,
        bins=30,
        alpha=0.55,
        label="Production",
    )

    ax.set_title(
        f"{selected_feature}: "
        "Reference vs Production"
    )

    ax.set_xlabel(
        selected_feature
    )

    ax.set_ylabel(
        "Frequency"
    )

    ax.legend()

    st.pyplot(
        fig
    )

    plt.close(
        fig
    )


# =========================================================
# Prediction Drift
# =========================================================

st.subheader(
    "🎯 Prediction Drift"
)


prediction_drift = report.get(
    "prediction_drift"
)


if prediction_drift:

    prediction_status = (
        prediction_drift.get(
            "status",
            "UNKNOWN",
        )
    )


    if prediction_status == "DRIFT":

        st.error(
            "🚨 Prediction Drift Detected"
        )

    elif prediction_status == "WARNING":

        st.warning(
            "⚠️ Prediction Drift Warning"
        )

    else:

        st.success(
            "✅ Prediction Distribution Stable"
        )


    # -----------------------------------------------------
    # Class distribution
    # -----------------------------------------------------

    class_distribution = (
        prediction_drift.get(
            "class_distribution",
            {},
        )
    )


    reference_prediction = (
        class_distribution.get(
            "reference",
            {},
        )
    )


    production_prediction = (
        class_distribution.get(
            "production",
            {},
        )
    )


    prediction_df = pd.DataFrame(
        {
            "Reference": pd.Series(
                reference_prediction
            ),
            "Production": pd.Series(
                production_prediction
            ),
        }
    )


    st.dataframe(
        prediction_df,
        use_container_width=True,
    )


    # -----------------------------------------------------
    # Prediction metrics
    # -----------------------------------------------------

    probability_drift = (
        prediction_drift.get(
            "probability_drift",
            {},
        )
    )


    psi_result = (
        probability_drift.get(
            "psi",
            {},
        )
    )


    ks_result = (
        probability_drift.get(
            "ks_test",
            {},
        )
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Prediction PSI",
            f"{psi_result.get('psi', 0):.4f}",
        )


    with col2:

        st.metric(
            "KS Statistic",
            f"{ks_result.get('statistic', 0):.4f}",
        )


    with col3:

        st.metric(
            "KS P-Value",
            f"{ks_result.get('p_value', 0):.4f}",
        )


# =========================================================
# Drifted Features
# =========================================================

drifted_features = report.get(
    "drifted_feature_names",
    [],
)


warning_features = report.get(
    "warning_feature_names",
    [],
)


if drifted_features:

    st.subheader(
        "🚨 Drifted Features"
    )

    for feature in drifted_features:

        st.error(
            f"Drift detected in **{feature}**"
        )


if warning_features:

    st.subheader(
        "⚠️ Warning Features"
    )

    for feature in warning_features:

        st.warning(
            f"Potential drift in **{feature}**"
        )


# =========================================================
# Download Report
# =========================================================

st.divider()

st.subheader(
    "📥 Export Monitoring Report"
)


report_json = json.dumps(
    report,
    indent=4,
)


st.download_button(
    label="⬇️ Download JSON Report",
    data=report_json,
    file_name="monitoring_report.json",
    mime="application/json",
    use_container_width=False,
)


# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "AI Model Drift Monitoring Platform | "
    "Data Drift + Prediction Drift | "
    "PSI + KS Statistical Monitoring"
)