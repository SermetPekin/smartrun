# examples/ml_test_script.py
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import lightgbm as lgb


def run_classification():
    # Load dataset
    iris = load_iris()
    X = iris.data
    y = iris.target
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Standardize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    # Initialize models
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=200),
        "SVM": SVC(),
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric="mlogloss"),
        "LightGBM": lgb.LGBMClassifier(),
    }
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, preds)
        print(f"Model: {name} - Accuracy: {acc:.4f}")
        print(classification_report(y_test, preds))


if __name__ == "__main__":
    run_classification()
