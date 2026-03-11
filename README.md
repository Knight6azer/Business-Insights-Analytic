# BGAI: Enterprise Predictive Analytics Suite

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.42+-ff4b4b.svg)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-orange.svg)
![Pydantic](https://img.shields.io/badge/pydantic-v2-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Version](https://img.shields.io/badge/version-3.0.0-purple.svg)

**BGAI (Business Growth AI)** is a full-stack, Python-native predictive intelligence platform. It bridges the gap between raw business data and actionable strategic foresight using advanced machine learning pipelines, real-time multi-chart visualization, and a secure multi-user backend.

---

## 🚀 System Capabilities

| Module | Features |
|:--|:--|
| **📊 Dashboard** | Live KPI metric cards, donut chart, activity timeline, system health panel |
| **📈 Analytics** | Date-range filters, 4-chart layout (pie, area, bar, box), stats table, CSV export |
| **🤖 Predictions** | 4 ML models, R²/MAE/RMSE metrics, cross-validation, 5-step forecast with confidence intervals |
| **📂 CRM** | Filter + region search, per-record delete, CSV export, inline data addition |
| **🔌 Integrations** | 8-service marketplace, toggle active/inactive, demo data generator |
| **⚙️ Settings** | Profile edit, password change + strength validation, JSON data export, danger-zone delete |

---

## 🤖 ML Engine — Model Support

| Model | Algorithm | Cross-Val | Best For |
|:--|:--|:--|:--|
| Linear Regression | OLS via Scikit-Learn | ✗ | Simple linear trends |
| Polynomial Regression | Degree-2 features + Ridge | ✗ | Non-linear curves |
| Random Forest | 200 trees, max_depth=6 | ✅ 5-fold | Medium-complexity datasets |
| Gradient Boosting | 150 estimators, lr=0.1 | ✅ 5-fold | High accuracy, small datasets |

All models return: **R² Score**, **MAE**, **RMSE**, and **5-step forecast with 95% confidence intervals**.

---

## 🛠️ Technology Stack

| Layer | Technology | Version |
|:--|:--|:--|
| **Frontend** | Streamlit | 1.42+ |
| **Backend** | Python | 3.13 |
| **Database** | SQLite + SQLAlchemy ORM | 2.x |
| **ML Engine** | Scikit-Learn | 1.4+ |
| **Security** | Passlib (PBKDF2 + bcrypt) + JWT | 1.7+ |
| **Validation** | Pydantic | v2 |
| **Visualization** | Plotly | 5.x |

---

## 🏁 Quick Start

### Prerequisites
- Python 3.10+
- pip package manager

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Knight6azer/Business-Insights-Analytic.git
cd Business-Insights-Analytic

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (copy and edit)
cp .env.example .env
# Set BGAI_SECRET_KEY in .env

# 5. Run the application
streamlit run BGAI.py
```

Navigate to `http://localhost:8501` — register an account to initialize the system.

> 💡 **Tip:** On first run, go to **Integrations → Generate Demo Data** and **Generate Demo Predictions** to instantly populate all charts and tables.

---

## 📁 Project Structure

```
BGAI/
├── BGAI.py                  # App entry point, global CSS, auth router
├── pages/
│   ├── 01_Dashboard.py      # KPI cards, activity charts, system health
│   ├── 02_Analytics.py      # Multi-chart analytics, filters, CSV export
│   ├── 03_Predictions.py    # ML model runner, metrics, forecast chart
│   ├── 04_CRM.py            # Business data CRUD, filters, export
│   ├── 05_Integrations.py   # Marketplace, demo data generator
│   └── 06_Settings.py       # Profile, password change, data export
├── backend/
│   ├── __init__.py
│   ├── auth.py              # JWT + PBKDF2 auth, password strength validator
│   ├── crud.py              # All database read/write/delete operations
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── main.py              # FastAPI REST API (decoupled backend)
│   ├── ml_engine.py         # ML training, evaluation, and forecasting
│   ├── models.py            # SQLAlchemy ORM models
│   └── schemas.py           # Pydantic v2 request/response schemas
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

## 🔒 Security Architecture

- **Password Hashing**: PBKDF2-SHA256 (primary) with bcrypt fallback via Passlib
- **Password Strength**: Enforced at registration — min 8 chars, uppercase, digit, special char
- **Session Tokens**: Signed JWT (HS256), 8-hour expiry, loaded from `.env`
- **DB Abstraction**: All queries via SQLAlchemy ORM — no raw SQL, no injection risk
- **Secret Key**: Loaded from `BGAI_SECRET_KEY` environment variable with runtime warning if default is used

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please follow **PEP 8** style guidelines and add docstrings to all new functions.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

---

*Architected by Ujjwal Tiwari · [GitHub](https://github.com/Knight6azer/Business-Insights-Analytic)*
