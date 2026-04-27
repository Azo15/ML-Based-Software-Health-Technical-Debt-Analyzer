"""
Module for training the ML model and estimating Technical Debt.
Uses RandomForestClassifier to predict bug-proneness and calculate
Health Score and Technical Debt Index.
"""
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from utils.logger import logger

class DebtEstimator:
    """
    Handles machine learning operations, technical debt estimation,
    and refactoring suggestions based on metrics.
    """

    def __init__(self):
        # We use a RandomForestClassifier as requested for robust estimation
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.features_col = [
            'cyclomatic_complexity', 'halstead_volume', 
            'halstead_difficulty', 'halstead_effort', 
            'loc', 'num_functions'
        ]
        self.is_trained = False

    def train(self, data: List[Dict[str, Any]]) -> str:
        """
        Trains the RandomForest model on the provided dataset.

        Args:
            data (List[Dict[str, Any]]): Dataset containing metrics and 'is_bug_fix' labels.

        Returns:
            str: Classification report string.
        """
        df = pd.DataFrame(data)
        
        # Ensure we have the necessary columns
        if not all(col in df.columns for col in self.features_col) or 'is_bug_fix' not in df.columns:
            logger.error("Dataset is missing required metric columns or labels.")
            raise ValueError("Invalid dataset structure for training.")

        X = df[self.features_col]
        y = df['is_bug_fix']

        if len(df) < 10:
            logger.warning("Very small dataset. Model performance might be poor.")

        # If only one class is present in the target, we can't train effectively
        if len(y.unique()) < 2:
            logger.warning("Only one class found in target 'is_bug_fix'. Creating a dummy model.")
            # Fallback for demonstration on tiny/clean repos
            self.is_trained = False
            return "Not enough class diversity to train model. (Need both bug-fix and non-bug-fix commits)"

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        logger.info("Training RandomForestClassifier...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, zero_division=0)
        logger.info("Model training completed successfully.")
        
        return report

    def estimate_debt(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Estimates the Health Score and Technical Debt Index for a given set of metrics.

        Args:
            metrics (Dict[str, float]): The software metrics of a file/function.

        Returns:
            Dict[str, Any]: Contains score, index, and refactoring suggestions.
        """
        # Convert metrics to DataFrame for prediction
        df_metrics = pd.DataFrame([metrics])[self.features_col]
        
        bug_probability = 0.5 # Default middle ground if not trained
        
        if self.is_trained:
            # predict_proba returns array of [prob_no_bug, prob_bug]
            proba = self.model.predict_proba(df_metrics)[0]
            if len(proba) > 1:
                bug_probability = proba[1]
            else:
                # Fallback if model somehow only learned one class
                bug_probability = 0.0 if self.model.classes_[0] == 0 else 1.0

        # Health Score Calculation (100 is best, 0 is worst)
        # We blend ML bug probability with direct metrics penalties
        base_score = (1.0 - bug_probability) * 100
        
        cc_penalty = min(metrics.get('cyclomatic_complexity', 0) * 1.5, 30)
        loc_penalty = min(metrics.get('loc', 0) * 0.05, 20)
        
        health_score = max(0, min(100, base_score - cc_penalty - loc_penalty))
        
        # Technical Debt Index Categorization
        if health_score >= 80:
            debt_index = "Low"
        elif health_score >= 50:
            debt_index = "Medium"
        else:
            debt_index = "High"

        # Generate Refactoring Suggestions
        suggestions = self._generate_suggestions(metrics)

        return {
            'health_score': round(health_score, 2),
            'technical_debt_index': debt_index,
            'bug_probability': round(bug_probability, 2),
            'refactoring_suggestions': suggestions
        }

    def _generate_suggestions(self, metrics: Dict[str, float]) -> List[str]:
        """
        Generates actionable refactoring suggestions based on metrics thresholds.
        """
        suggestions = []
        
        cc = metrics.get('cyclomatic_complexity', 0)
        if cc > 10:
            suggestions.append(f"High Cyclomatic Complexity ({cc:.1f}): Consider splitting large functions to reduce execution paths.")
            
        loc = metrics.get('loc', 0)
        if loc > 300:
            suggestions.append(f"Large File Size ({loc} LOC): The file is getting too large. Consider extracting logic into separate modules.")
            
        difficulty = metrics.get('halstead_difficulty', 0)
        if difficulty > 50:
            suggestions.append(f"High Halstead Difficulty ({difficulty:.1f}): The code is dense and hard to understand. Add detailed docstrings and simplify expressions.")
            
        if not suggestions:
            suggestions.append("Code looks healthy! Keep up the good work.")
            
        return suggestions
