from typing import Dict, List

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Dataset information
# ---------------------------------------------------------

class DatasetInfo(BaseModel):

    reference_rows: int = Field(
        ge=0
    )

    production_rows: int = Field(
        ge=0
    )

    features_monitored: int = Field(
        ge=0
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

class MonitoringSummary(BaseModel):

    total_features: int = Field(
        ge=0
    )

    drifted_features: int = Field(
        ge=0
    )

    warning_features: int = Field(
        ge=0
    )

    healthy_features: int = Field(
        ge=0
    )


# ---------------------------------------------------------
# KS Test
# ---------------------------------------------------------

class KSTestResult(BaseModel):

    statistic: float

    p_value: float

    status: str


# ---------------------------------------------------------
# Feature result
# ---------------------------------------------------------

class FeatureDriftResult(BaseModel):

    status: str

    psi: float

    psi_status: str

    ks_test: KSTestResult

    missing_values: Dict


# ---------------------------------------------------------
# Prediction PSI
# ---------------------------------------------------------

class PredictionPSI(BaseModel):

    psi: float

    status: str


# ---------------------------------------------------------
# Prediction drift
# ---------------------------------------------------------

class PredictionDriftResult(BaseModel):

    status: str

    class_distribution: Dict[str, Dict[str, float]]

    probability_drift: Dict


# ---------------------------------------------------------
# Complete monitoring response
# ---------------------------------------------------------

class MonitoringResponse(BaseModel):

    status: str

    dataset: DatasetInfo

    summary: MonitoringSummary

    drifted_feature_names: List[str]

    warning_feature_names: List[str]

    features: Dict[str, FeatureDriftResult]

    prediction_drift: PredictionDriftResult | None = None