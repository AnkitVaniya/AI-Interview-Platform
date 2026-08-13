"""
Predicts which difficulty level (easy/medium/hard) a user is ready for,
based on their accuracy and average attempts-per-solve.

Trained on synthetic data at startup for a working demo out of the box.
Swap `_generate_training_data()` for a query against real `submissions` +
`user_topic_progress` rows once you have enough production data — the
model-fitting code below doesn't need to change, only the data source.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

_LABELS = ["easy", "medium", "hard"]


def _generate_training_data(n_per_class: int = 200, seed: int = 42):
    rng = np.random.default_rng(seed)

    # easy-ready: low accuracy, many attempts per solve
    easy = rng.normal(loc=[0.35, 4.0], scale=[0.1, 1.0], size=(n_per_class, 2))
    # medium-ready: moderate accuracy, moderate attempts
    medium = rng.normal(loc=[0.65, 2.0], scale=[0.1, 0.5], size=(n_per_class, 2))
    # hard-ready: high accuracy, few attempts per solve
    hard = rng.normal(loc=[0.85, 1.2], scale=[0.08, 0.3], size=(n_per_class, 2))

    X = np.vstack([easy, medium, hard])
    X[:, 0] = np.clip(X[:, 0], 0, 1)
    X[:, 1] = np.clip(X[:, 1], 1, 10)
    y = np.array([0] * n_per_class + [1] * n_per_class + [2] * n_per_class)
    return X, y


class DifficultyPredictor:
    def __init__(self):
        X, y = _generate_training_data()
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, y)

    def predict(self, accuracy: float, avg_attempts_per_solve: float) -> dict:
        features = np.array([[accuracy, avg_attempts_per_solve]])
        pred_idx = self.model.predict(features)[0]
        probs = self.model.predict_proba(features)[0]
        return {
            "recommended_difficulty": _LABELS[pred_idx],
            "confidence": round(float(probs[pred_idx]), 2),
        }


# module-level singleton — trained once at import time, reused across requests
difficulty_predictor = DifficultyPredictor()
