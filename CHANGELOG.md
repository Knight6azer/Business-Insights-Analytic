# Changelog

All notable changes to **BGAI** are documented here.
This project follows [Semantic Versioning](https://semver.org/).

---

## [3.0.0] — March 2026

### ✨ Added
- **ML Engine (v3)**: Added Polynomial Regression and Gradient Boosting models
- **ML Metrics**: Real R², MAE, RMSE metrics computed from train/test split
- **Cross-Validation**: 5-fold CV for Random Forest and Gradient Boosting
- **Confidence Intervals**: 5-step forecast with ±95% confidence band on chart
- **Dashboard KPIs**: Live animated metric cards driven from database aggregate
- **Dashboard Charts**: Donut pie + area upload-timeline chart
- **Dashboard Activity**: Dual recent-activity tables with status badges
- **Dashboard Health**: System health panel (Database, ML Engine, Auth status)
- **Analytics Filters**: Sidebar date-range + type filter with live DataFrame refresh
- **Analytics Charts**: Box plot for value distribution, regional bar chart
- **Analytics Stats**: Summary statistics table grouped by data type
- **Analytics Export**: Download filtered data as CSV
- **Predictions UI**: Model selector card grid with descriptions and color coding
- **Predictions History**: Status filter, per-item delete, mini forecast chart
- **CRM Filter**: Type and region filter bar with real-time update
- **CRM Export**: Export all records to CSV
- **CRM Delete**: Per-record delete via dropdown selector
- **Integrations Marketplace**: 8-service card grid (Salesforce, HubSpot, Slack, Sheets, Stripe, GitHub, Zapier, Custom API)
- **Integrations Toggle**: Active/inactive toggle for connected services
- **Integrations Demo**: "Generate 5 Demo Predictions" quick action button
- **Settings Profile**: Editable Name and Company fields, saved to database
- **Settings Security**: Password change form with current password verification
- **Settings Data Export**: Full JSON export of all user data and predictions
- **Settings Danger Zone**: Delete all business data with typed confirmation
- **Settings About**: Tech stack and build info tables
- **Auth**: Password strength validation (uppercase, digit, special char, min 8 chars)
- **Auth**: `BGAI_SECRET_KEY` loaded from `.env` via `python-dotenv`
- **Auth**: `last_login` timestamp stamped on every successful login
- **CRUD**: `delete_business_data`, `delete_all_user_data`, `delete_prediction`
- **CRUD**: `get_user_stats` returning aggregated KPI counts
- **CRUD**: `toggle_integration`, `update_user`, `change_password`, `update_last_login`
- **Models**: `last_login` column on `User`
- **Models**: `accuracy_score` column on `Prediction`
- **Models**: `description` column on `BusinessData`
- **Schemas**: Upgraded to Pydantic v2 (`ConfigDict`, `field_validator`)
- **Schemas**: Added `UserUpdate`, `DashboardSummary`, `MetricsSchema`, `TokenData`

### 🛠 Changed
- `ml_engine.py`: 3-step forecast → 5-step forecast with confidence intervals
- `ml_engine.py`: Mock confidence → confidence derived from R² score
- `auth.py`: Token expiry 300 min → 480 min (8 hours)
- `BGAI.py`: Login page redesigned with hero header, feature pills, and 2-col register form
- `BGAI.py`: Post-login home shows live DB-backed KPI strip and module overview cards
- `requirements.txt`: Pinned library versions, organized by category

### 🗑 Removed
- Hardcoded `SECRET_KEY` string from `auth.py` (moved to `.env`)

---

## [2.5.0] — February 2026

### ✨ Added
- Glassmorphism CSS theme with neon buttons and custom sidebar
- Plotly integration for interactive charts
- Random Forest and Linear Regression prediction models
- CRM data entry form with structured JSON storage
- Integration management (add, list)
- Settings page with static profile display

### 🛠 Changed
- Upgraded from plain Streamlit columns to tabbed navigation on predictions and CRM pages

---

## [2.0.0] — January 2026

### ✨ Added
- FastAPI backend in `backend/main.py` with JWT-protected REST endpoints
- SQLAlchemy ORM models: `User`, `BusinessData`, `Prediction`, `Feedback`, `Integration`
- Pydantic v1 schemas for all request/response DTOs
- Passlib PBKDF2-SHA256 password hashing
- Multi-page Streamlit app with 6 pages

### 🛠 Changed
- Monolithic script → modular pages + backend package

---

## [1.0.0] — December 2025

### 🎉 Initial Release
- Single-file Streamlit prototype
- Basic login/register without password hashing
- Static demo data display
- Single linear regression model
