"""Fixed holdout comparisons; the test period never selects the deployed model."""

import math

import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_fscore_support


def ranking_metrics(labels, scores, predictions=None):
    """Measure ranking with a fixed inspection budget of 20% of revisions.

    Average precision is the step-weighted PR summary, not trapezoidal PR AUC.
    Tied scores retain the deterministic input order.
    """
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if len(labels) == 0 or len(labels) != len(scores):
        raise ValueError("Labels and scores must have equal, nonzero length")
    if not np.isin(labels, [0, 1]).all() or not np.isfinite(scores).all():
        raise ValueError("Labels must be binary and scores must be finite")
    k = max(1, math.ceil(len(labels) * 0.2))
    top = np.argsort(-scores, kind="stable")[:k]
    positives = int(labels.sum())
    result = {
        "average_precision": float(average_precision_score(labels, scores)) if positives else None,
        "inspection_k": k,
        "recall_at_k": float(labels[top].sum() / positives) if positives else None,
        "precision_at_k": float(labels[top].mean()),
    }
    if predictions is not None:
        precision, recall, f1, _ = precision_recall_fscore_support(
            labels, predictions, average="binary", zero_division=0
        )
        result.update(precision=float(precision), recall=float(recall), f1=float(f1))
    return result
