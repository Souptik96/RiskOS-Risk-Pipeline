import lightgbm as lgb
import numpy as np
from typing import Dict, Any
from .schemas import Transaction

class RiskScorer:
    def __init__(self, model_path: str = "model_artifacts/risk_lgbm.txt"):
        self.model = lgb.Booster(model_file=model_path)
        self.feature_order = [
            'amount', 'hour_of_day', 'is_cross_border', 'merchant_risk_tier',
            'velocity_1h', 'amount_vs_user_avg', 'account_age_days',
            'failed_auth_count', 'device_seen_before', 'country_risk_score'
        ]
    
    def score(self, transaction: Transaction) -> float:
        """Score a transaction using LightGBM model"""
        # Convert transaction to feature vector
        features = self._extract_features(transaction)
        
        # Reshape for prediction (1 sample)
        features = features.reshape(1, -1)
        
        # Get prediction (probability of class 1)
        pred = self.model.predict(features, num_iteration=self.model.best_iteration)
        
        # Return risk score (probability)
        return float(pred[0])
    
    def _extract_features(self, transaction: Transaction) -> np.ndarray:
        """Extract features from transaction in correct order"""
        features = []
        for feature in self.feature_order:
            value = getattr(transaction, feature)
            if isinstance(value, bool):
                features.append(1.0 if value else 0.0)
            else:
                features.append(float(value))
        
        return np.array(features)
    
    def batch_score(self, transactions: list) -> np.ndarray:
        """Score multiple transactions at once"""
        feature_matrix = []
        for transaction in transactions:
            features = self._extract_features(transaction)
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        predictions = self.model.predict(feature_matrix, num_iteration=self.model.best_iteration)
        
        return predictions