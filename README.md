# 🚀 AI Model Drift Detection Platform

An end-to-end **Machine Learning Model Monitoring and Drift Detection Platform** built with Python, FastAPI, Streamlit, Scikit-learn, and SQLAlchemy.

This platform helps monitor machine learning systems in production by detecting **Data Drift** and **Prediction Drift**, generating alerts, storing monitoring history, and providing an interactive dashboard for model health monitoring.

---

## 📌 Overview

Machine learning models can become less reliable when production data changes compared to the data used during model development.

This project provides a monitoring solution that compares production data against reference data and identifies potential changes in data and model prediction behavior.

The platform supports:

* Data Drift Detection
* Prediction Drift Detection
* Production CSV Validation
* Monitoring Reports
* Automated Alerts
* Monitoring History
* SQLite Database Storage
* Automated Monitoring Scheduler
* REST API
* Interactive Dashboard

---

## ✨ Features

### 🔍 Data Drift Detection

Compares reference data with production data to identify changes in feature distributions.

### 📈 Prediction Drift Detection

Monitors changes in model prediction behavior between reference and production data.

### 🚨 Alert System

Generates alerts when significant drift or warning conditions are detected.

### 🕒 Monitoring History

Stores previous monitoring results so model behavior can be tracked over time.

### 🗄️ Database Monitoring

Monitoring runs and alerts can be stored in a SQLite database using SQLAlchemy.

### ⏰ Automated Scheduler

The platform supports scheduled monitoring with configurable monitoring intervals.

### 📊 Interactive Dashboard

A Streamlit dashboard provides a visual interface for monitoring model health and drift results.

### ⚡ FastAPI Backend

Provides REST API endpoints for monitoring, reports, history, scheduler control, database records, and alerts.

---

# 🏗️ Architecture

```text
                    Production CSV
                         │
                         ▼
                ┌─────────────────┐
                │ Data Validation │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Drift Detection │
                └────────┬────────┘
                         │
                ┌────────┴────────┐
                ▼                 ▼
        ┌──────────────┐  ┌───────────────┐
        │  Data Drift  │  │ Prediction    │
        │  Detection   │  │ Drift         │
        └──────┬───────┘  └───────┬───────┘
               │                  │
               └────────┬─────────┘
                        ▼
               ┌──────────────────┐
               │ Monitoring Report│
               └────────┬─────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      ┌────────┐   ┌─────────┐   ┌─────────┐
      │ Alerts │   │ History │   │ Database│
      └────────┘   └─────────┘   └─────────┘
          │             │             │
          └─────────────┼─────────────┘
                        ▼
              ┌────────────────────┐
              │ Streamlit Dashboard│
              └────────────────────┘
```

---

# 🛠️ Technology Stack

| Technology   | Purpose                   |
| ------------ | ------------------------- |
| Python       | Core programming language |
| FastAPI      | REST API backend          |
| Uvicorn      | ASGI server               |
| Streamlit    | Monitoring dashboard      |
| Pandas       | Data processing           |
| NumPy        | Numerical computing       |
| Scikit-learn | Machine learning          |
| SciPy        | Statistical analysis      |
| Joblib       | Model serialization       |
| SQLAlchemy   | Database ORM              |
| SQLite       | Monitoring data storage   |
| APScheduler  | Automated scheduling      |
| Matplotlib   | Data visualization        |
| Altair       | Dashboard visualization   |
| Pytest       | Testing                   |

---

# 📁 Project Structure

```text
ai-model-drift-platform/
│
├── app/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── crud.py
│   │
│   ├── drift/
│   │   ├── data_drift.py
│   │   └── prediction_drift.py
│   │
│   ├── services/
│   │   ├── baseline_service.py
│   │   ├── monitoring_service.py
│   │   ├── monitoring_history.py
│   │   ├── alert_service.py
│   │   ├── database_monitoring_service.py
│   │   └── scheduler_service.py
│   │
│   ├── schemas/
│   │   └── monitoring.py
│   │
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── reference/
│   │   └── reference.csv
│   └── production/
│       └── production.csv
│
├── model/
│   ├── churn_model.joblib
│   └── reference_baseline.json
│
├── reports/
│   ├── latest_report.json
│   └── history.json
│
├── scripts/
│   ├── train_model.py
│   ├── test_drift.py
│   └── test_prediction_drift.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 📊 Required Production Features

The production CSV must contain these features:

```text
age
monthly_income
account_balance
login_frequency
support_tickets
```

The API validates:

* CSV file format
* Empty datasets
* Minimum number of rows
* Required columns
* Numeric feature values
* Infinite values

The production dataset must contain at least **50 rows**.

---

# 🔌 API Endpoints

## Health Check

```http
GET /health
```

Returns the current API health status.

Example:

```json
{
  "status": "healthy",
  "service": "AI Model Drift Detection Platform"
}
```

---

## Root Endpoint

```http
GET /
```

Returns basic application information.

Example:

```json
{
  "message": "AI Model Drift Detection Platform",
  "status": "running",
  "version": "1.0.0"
}
```

---

## Reference Baseline

```http
GET /baseline
```

Returns the reference baseline used for drift monitoring.

---

## Monitor Production Data

```http
POST /monitor
```

Upload a production CSV file and run the complete monitoring pipeline.

The pipeline performs:

```text
Upload CSV
    ↓
Validate Data
    ↓
Load Reference Data
    ↓
Detect Data Drift
    ↓
Detect Prediction Drift
    ↓
Build Monitoring Report
    ↓
Generate Alerts
    ↓
Save History
    ↓
Save Database Record
    ↓
Save Latest Report
```

Example:

```bash
curl -X POST "http://127.0.0.1:8000/monitor" \
-F "file=@production.csv"
```

---

## Monitoring History

```http
GET /history
```

Returns recent monitoring history.

Example:

```text
/history?limit=20
```

---

## Latest Report

```http
GET /report
```

Returns the latest monitoring report.

---

# ⏰ Scheduler API

## Scheduler Status

```http
GET /scheduler/status
```

Returns the current scheduler status.

---

## Start Scheduler

```http
POST /scheduler/start
```

Example:

```text
/scheduler/start?interval_minutes=60
```

The application also starts automated monitoring with a default interval of **60 minutes** when the FastAPI application starts.

---

## Stop Scheduler

```http
POST /scheduler/stop
```

Stops the monitoring scheduler.

---

# 🗄️ Database API

## Get Monitoring Runs

```http
GET /database/runs
```

Returns monitoring runs stored in the database.

Example:

```text
/database/runs?limit=50
```

---

## Get Single Monitoring Run

```http
GET /database/runs/{run_id}
```

Example:

```text
/database/runs/1
```

Returns detailed information about a specific monitoring run, including associated alerts.

---

## Get Alerts

```http
GET /database/alerts
```

Returns alerts stored in the database.

Example:

```text
/database/alerts?limit=100
```

---

# 📄 Monitoring Report

A monitoring report can contain:

* Overall monitoring status
* Data drift results
* Prediction drift results
* Drifted features
* Warning features
* Healthy features
* Reference dataset statistics
* Production dataset statistics
* Generated alerts
* Monitoring timestamp

Latest report:

```text
reports/latest_report.json
```

Monitoring history:

```text
reports/history.json
```

---

# ▶️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-model-drift-platform.git
```

```bash
cd ai-model-drift-platform
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🚀 Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```


# 🚀 FastAPI Backend ScreenShot

<img width="941" height="428" alt="s1" src="https://github.com/user-attachments/assets/118809ef-7b93-4a8e-8078-366e98fa1430" />

<img width="943" height="428" alt="s2" src="https://github.com/user-attachments/assets/79206772-adbb-4248-9270-6209925acdfd" />

---


# 📊 Run Streamlit Dashboard

Open another terminal:

```bash
streamlit run dashboard/app.py
```

# 📊 Streamlit Dashboard ScreenShot

<img width="947" height="432" alt="s3" src="https://github.com/user-attachments/assets/1dafe1a7-56b3-468d-ab39-4f77e6ca93f6" />
<img width="945" height="413" alt="s4" src="https://github.com/user-attachments/assets/17768ba7-42e4-49bf-9f03-c858e4432416" />
<img width="937" height="472" alt="s5" src="https://github.com/user-attachments/assets/70aeee21-d159-4288-a05f-06e350ac81a4" />
<img width="950" height="451" alt="s6" src="https://github.com/user-attachments/assets/adb0479b-e1c5-4c38-b3ed-d9141915fcf1" />
<img width="957" height="390" alt="s7" src="https://github.com/user-attachments/assets/1224f06a-798d-44ec-a3fe-e4e2aa298c98" />
<img width="932" height="438" alt="s8" src="https://github.com/user-attachments/assets/9d4e3bcd-129c-4fea-812c-aa4701ac4f58" />

---

# 🧪 Testing

Run data drift tests:

```bash
python scripts/test_drift.py
```

Run prediction drift tests:

```bash
python scripts/test_prediction_drift.py
```

Run the complete test suite:

```bash
pytest
```

---

# 🤖 Model

The project uses a machine learning churn model:

```text
model/churn_model.joblib
```

The reference baseline is stored in:

```text
model/reference_baseline.json
```

---

# 🔄 Monitoring Lifecycle

```text
Reference Dataset
       │
       ▼
Reference Baseline
       │
       ▼
Production Dataset
       │
       ▼
Data Validation
       │
       ▼
Data Drift Detection
       │
       ▼
Prediction Drift Detection
       │
       ▼
Health Status
       │
       ▼
Alerts
       │
       ▼
Monitoring History
       │
       ▼
SQLite Database
       │
       ▼
Streamlit Dashboard
```

---

# 🎯 Use Cases

This platform can be adapted for monitoring:

* Customer Churn Models
* Fraud Detection Models
* Credit Risk Models
* Recommendation Systems
* Customer Classification Models
* Financial Prediction Models
* Production ML Pipelines

---

# 🔮 Future Improvements

* Docker deployment
* PostgreSQL integration
* Cloud deployment
* Email notifications
* Slack notifications
* Real-time monitoring
* Authentication and authorization
* Multi-model monitoring
* CI/CD integration
* Kubernetes deployment
* Advanced drift visualization

---

# 👨‍💻 Author

## Sohail Akhter

**Python Developer | AI/ML Engineer**

Interested in:

* Artificial Intelligence
* Machine Learning
* MLOps
* Python Development
* AI Automation

---

## ⭐ Project

If you find this project useful, consider giving it a ⭐ on GitHub.
