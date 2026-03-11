"""
ml_engine.py — BGAI Machine Learning Engine
============================================
Handles training, evaluation, and forecasting for all supported model types.
Implements proper train/test split, cross-validation, and real performance metrics.

Author: Ujjwal Tiwari
Version: 3.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _prepare_dataframe(input_data: Dict[str, Any]) -> Tuple[pd.DataFrame, str]:
    """
    Parse the input dictionary and return a cleaned DataFrame plus
    the name of the detected numeric target column.

    Parameters
    ----------
    input_data : dict
        Must contain a ``values`` key whose value is a list of dicts.

    Returns
    -------
    df : pd.DataFrame
    target_col : str
    """
    if not input_data or "values" not in input_data:
        raise ValueError("Invalid input format. Expected {'values': [...]}")

    df = pd.DataFrame(input_data["values"])
    if df.empty:
        raise ValueError("Dataset is empty — please provide at least 3 records.")

    df["_idx"] = range(len(df))

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    target_col = next((c for c in numeric_cols if c != "_idx"), None)
    if not target_col:
        raise ValueError("No numeric target column found in the dataset.")

    return df, target_col


def _confidence_interval(predictions: np.ndarray, residuals: np.ndarray, z: float = 1.96) -> List[Dict]:
    """
    Return forecast steps with ±95 % confidence intervals based on residual std.
    """
    std = residuals.std() if len(residuals) > 1 else abs(predictions.mean() * 0.05)
    result = []
    for i, val in enumerate(predictions, start=1):
        result.append({
            "step": i,
            "value": round(float(val), 2),
            "lower": round(float(val - z * std), 2),
            "upper": round(float(val + z * std), 2),
        })
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train_and_predict(model_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Train the selected model on the provided data and return a 5-step forecast
    along with evaluation metrics.

    Parameters
    ----------
    model_type : str
        One of ``"Linear Regression"``, ``"Polynomial Regression"``,
        ``"Random Forest"``, ``"Gradient Boosting"``.
    input_data : dict
        ``{"values": [{"x": 1, "y": 10}, ...]}``.

    Returns
    -------
    dict
        Keys: ``model_type``, ``target_column``, ``metrics``, ``forecast``,
        ``confidence``, ``feature_importances`` (RF / GB only),
        ``training_samples``, ``test_samples``.
    """
    try:
        df, target_col = _prepare_dataframe(input_data)

        X = df[["_idx"]].values
        y = df[target_col].values

        # Require at least 4 rows for a meaningful split
        if len(df) < 4:
            X_train, X_test, y_train, y_test = X, X, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        # ---- Model selection --------------------------------------------------
        scaler = StandardScaler()
        feature_importances: Dict[str, float] = {}

        if "Polynomial" in model_type:
            pipeline = Pipeline([
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("scaler", scaler),
                ("model", Ridge(alpha=1.0)),
            ])
        elif "Random Forest" in model_type:
            pipeline = Pipeline([
                ("scaler", scaler),
                ("model", RandomForestRegressor(
                    n_estimators=200, max_depth=6, random_state=42, n_jobs=-1
                )),
            ])
        elif "Gradient Boosting" in model_type:
            pipeline = Pipeline([
                ("scaler", scaler),
                ("model", GradientBoostingRegressor(
                    n_estimators=150, learning_rate=0.1, max_depth=4, random_state=42
                )),
            ])
        else:
            # Default: Linear Regression
            pipeline = Pipeline([
                ("scaler", scaler),
                ("model", LinearRegression()),
            ])

        # ---- Training & Evaluation -------------------------------------------
        pipeline.fit(X_train, y_train)
        y_pred_test = pipeline.predict(X_test)
        y_pred_train = pipeline.predict(X_train)
        residuals = y_test - y_pred_test

        r2  = r2_score(y_test, y_pred_test)
        mae = mean_absolute_error(y_test, y_pred_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))

        # Cross-validation on full dataset (5-fold) for ensemble models
        cv_score = None
        if ("Random Forest" in model_type or "Gradient Boosting" in model_type) and len(df) >= 5:
            cv_scores = cross_val_score(pipeline, X, y, cv=min(5, len(df)), scoring="r2")
            cv_score = round(float(cv_scores.mean()), 4)

        # Feature importances (tree models)
        inner = pipeline.named_steps.get("model")
        if hasattr(inner, "feature_importances_"):
            feature_importances = {"_idx": round(float(inner.feature_importances_[0]), 4)}

        # ---- Forecast --------------------------------------------------------
        last_idx = int(df["_idx"].max())
        future_X = np.array([[last_idx + i] for i in range(1, 6)])
        future_preds = pipeline.predict(future_X)
        forecast = _confidence_interval(future_preds, residuals)

        # Simple confidence proxy (capped between 0.5 and 0.99)
        confidence = min(0.99, max(0.5, round(float(r2) if r2 > 0 else 0.5, 4)))

        return {
            "model_type": model_type,
            "target_column": target_col,
            "training_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "metrics": {
                "r2_score": round(float(r2), 4),
                "mae": round(float(mae), 4),
                "rmse": round(float(rmse), 4),
                "cv_r2_mean": cv_score,
            },
            "forecast": forecast,
            "confidence": confidence,
            "feature_importances": feature_importances,
        }

    except ValueError as ve:
        return {"error": str(ve)}
    except Exception as exc:
        return {"error": f"ML Engine Error: {str(exc)}"}
