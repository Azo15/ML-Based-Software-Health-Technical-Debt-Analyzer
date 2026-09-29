"""File risk ranking and separate, rule-based maintainability findings."""

from typing import Any, Dict, List, Optional

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, classification_report


class DebtEstimator:
    """Retained name for CLI compatibility; risk is distinct from debt findings.

    A Random Forest score is useful for ranking. It is not displayed as a
    calibrated defect probability. The candidate labels are noisy signals from
    future fix-message commits, not confirmed bug ground truth.
    """

    features_col = [
        "cyclomatic_complexity",
        "cyclomatic_complexity_max",
        "halstead_volume",
        "halstead_difficulty",
        "halstead_effort",
        "loc",
        "num_functions",
    ]

    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        self.train_commits: List[str] = []
        self.test_commits: List[str] = []

    def train(self, data: List[Dict[str, Any]]) -> str:
        """Train on earlier commits and evaluate on later, untouched commits."""
        self.is_trained = False
        self.train_commits = []
        self.test_commits = []
        if len(data) < 10:
            return "Model unavailable: at least 10 labeled file revisions are required."

        required = set(self.features_col) | {
            "future_bug_fix", "commit_hash", "commit_date", "commit_sequence",
            "label_observed_at_sequence", "path",
        }
        if any(not required.issubset(row) for row in data):
            raise ValueError("Dataset is missing required features, provenance, or future labels")

        df = pd.DataFrame(data)
        pd.to_datetime(df["commit_date"], utc=True, errors="raise")
        df = df.sort_values(["commit_sequence"], kind="stable")
        commit_order = df["commit_hash"].drop_duplicates().tolist()
        if len(commit_order) < 5:
            return "Model unavailable: at least five distinct commits are required."

        cutoff = max(1, int(len(commit_order) * 0.8))
        self.train_commits = commit_order[:cutoff]
        self.test_commits = commit_order[cutoff:]
        first_test_sequence = int(df.loc[df["commit_hash"] == self.test_commits[0], "commit_sequence"].iloc[0])
        # A training label is usable only if its entire future observation
        # window ended before the first held-out commit.
        train = df[
            df["commit_hash"].isin(self.train_commits)
            & (df["label_observed_at_sequence"] < first_test_sequence)
        ]
        test = df[df["commit_hash"].isin(self.test_commits)]
        self.train_commits = train["commit_hash"].drop_duplicates().tolist()
        if len(train) < 5:
            return "Model unavailable: fewer than five training revisions remain after the time boundary."
        if train["future_bug_fix"].nunique() < 2 or test["future_bug_fix"].nunique() < 2:
            return "Model unavailable: both time periods need fix and non-fix examples."

        X_train = train[self.features_col].apply(pd.to_numeric, errors="raise")
        X_test = test[self.features_col].apply(pd.to_numeric, errors="raise")
        if X_train.isna().any().any() or X_test.isna().any().any():
            raise ValueError("Dataset contains missing numeric features")

        self.model.fit(X_train, train["future_bug_fix"])
        predictions = self.model.predict(X_test)
        positive_column = list(self.model.classes_).index(1)
        scores = self.model.predict_proba(X_test)[:, positive_column]
        self.is_trained = True
        report = classification_report(test["future_bug_fix"], predictions, zero_division=0)
        average_precision = average_precision_score(test["future_bug_fix"], scores)
        return (
            f"Time holdout: {len(train)} train and {len(test)} test revisions; "
            f"{len(self.train_commits)} train and {len(self.test_commits)} test commits "
            f"after excluding labels observed in the test period.\n"
            f"Average precision (PR AUC): {average_precision:.3f}\n{report}"
        )

    def estimate_debt(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Return ranking score and independent maintainability findings."""
        risk_score: Optional[float] = None
        if self.is_trained:
            features = pd.DataFrame([metrics])[self.features_col]
            positive_column = list(self.model.classes_).index(1)
            risk_score = round(float(self.model.predict_proba(features)[0][positive_column]), 3)

        findings = self._maintainability_findings(metrics)
        return {
            "risk_score": risk_score,
            "risk_score_kind": "relative_ranking_not_calibrated_probability" if risk_score is not None else "unavailable",
            "maintainability_findings": findings,
        }

    @staticmethod
    def _maintainability_findings(metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        findings: List[Dict[str, str]] = []
        maximum_complexity = metrics.get("cyclomatic_complexity_max", 0)
        if maximum_complexity > 10:
            findings.append({
                "rule": "complex_function",
                "reason": f"Most complex function has cyclomatic complexity {maximum_complexity:.1f} (>10)",
                "suggestion": "Review the function's branches and extract coherent steps with tests.",
            })
        loc = metrics.get("loc", 0)
        if loc > 300:
            findings.append({
                "rule": "large_file",
                "reason": f"File has {loc:.0f} non-comment lines (>300)",
                "suggestion": "Review whether distinct responsibilities can be moved into smaller modules.",
            })
        difficulty = metrics.get("halstead_difficulty", 0)
        if difficulty > 50:
            findings.append({
                "rule": "dense_expressions",
                "reason": f"Halstead difficulty is {difficulty:.1f} (>50)",
                "suggestion": "Simplify dense expressions and name intermediate concepts.",
            })
        return findings
