from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.database import (
    Base,
)


# =========================================================
# Monitoring Run Model
# =========================================================

class MonitoringRun(Base):

    __tablename__ = (
        "monitoring_runs"
    )


    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )


    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    status = Column(
        String,
        nullable=False,
    )


    total_features = Column(
        Integer,
        default=0,
    )


    drifted_features = Column(
        Integer,
        default=0,
    )


    warning_features = Column(
        Integer,
        default=0,
    )


    healthy_features = Column(
        Integer,
        default=0,
    )


    reference_rows = Column(
        Integer,
        default=0,
    )


    production_rows = Column(
        Integer,
        default=0,
    )


    prediction_drift = Column(
        String,
        nullable=True,
    )


    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    alerts = relationship(
        "Alert",
        back_populates="monitoring_run",
        cascade="all, delete-orphan",
    )


# =========================================================
# Alert Model
# =========================================================

class Alert(Base):

    __tablename__ = "alerts"


    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )


    monitoring_run_id = Column(
        Integer,
        ForeignKey(
            "monitoring_runs.id"
        ),
        nullable=False,
    )


    severity = Column(
        String,
        nullable=False,
    )


    type = Column(
        String,
        nullable=False,
    )


    feature = Column(
        String,
        nullable=True,
    )


    message = Column(
        String,
        nullable=False,
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


    # -----------------------------------------------------
    # Relationship
    # -----------------------------------------------------

    monitoring_run = relationship(
        "MonitoringRun",
        back_populates="alerts",
    )