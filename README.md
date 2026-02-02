# BGAI: Enterprise Predictive Analytics Suite

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.13+-blue.svg) ![Streamlit](https://img.shields.io/badge/streamlit-1.42+-ff4b4b.svg) ![Status](https://img.shields.io/badge/status-production-success.svg)

**BGAI (Business Growth AI)** is a high-performance, Python-native predictive intelligence platform. It bridges the critical gap between raw business data and actionable strategic foresight, utilizing advanced machine learning pipelines and real-time visualization engines.

## 🚀 System Capabilities

### 1. Advanced Analytics Engine
- **Real-time Visualization**: Interactive, low-latency plotting utilizing Plotly.
- **Multi-Dimensional Analysis**: Granular data slicing by region, sector, or custom KPIs.
- **Trend Detection**: Automated anomaly detection algorithms.

### 2. ML & Prediction Layer
- **Automated Pipelines**: Scikit-Learn integration for auto-tuning hyperparameters.
- **Ensemble Modeling**: Utilizes Random Forest and Regressors for robust forecasting.
- **Confidence Scoring**: Transparent uncertainty quantification for every prediction.

### 3. CRM & Data Persistence
- **ACID Compliance**: Transactional integrity powered by SQLAlchemy ORM.
- **Secure Authentication**: PBKDF2 with SHA-256 hashing and JWT session management.
- **Cyber-Aesthetic UI**: A modern, glassmorphism-based interface designed for deep immersion.

### 4. Extensibility
- **Modular Architecture**: Decoupled backend logic (FastAPI pattern) allows for seamless API integration.
- **Plugin System**: Ready for Salesforce, HubSpot, and custom REST data sources.

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Python-based reactive UI framework |
| **Backend** | Python 3.13 | Core business logic and orchestration |
| **Database** | SQLite / SQLAlchemy | Local relational database with ORM |
| **ML Engine** | Scikit-Learn | Predictive modeling and statistical analysis |
| **Security** | Passlib (PBKDF2) | Cryptographic hashing and auth flow |

## 🏁 Quick Start

### Prerequisites
- Python 3.10+
- Pip package manager

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Knight6azer/Business-Insights-Analytic.git
    cd Business-Insights-Analytic
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run BGAI.py
    ```

4.  **Access the Dashboard**
    - Navigate to `http://localhost:8501`.
    - Register a new admin account to initialize the system.

## 📁 Project Structure

```bash
BGAI/
├── BGAI.py                 # Application Entry Point & Dashboard
├── pages/                  # Streamlit modular pages
│   ├── 02_Analytics.py     # Visualization Engine
│   ├── 03_Predictions.py   # ML Inference Interface
│   └── ...
├── backend/                # Core Business Logic
│   ├── auth.py             # Security & JWT
│   ├── ml_engine.py        # Prediction Pipelines
│   ├── models.py           # Database Schema (ORM)
│   └── ...
└── site.db                 # Local SQLite instance (Gitignored recommended)
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Architected by Ujjwal Tiwari.*
