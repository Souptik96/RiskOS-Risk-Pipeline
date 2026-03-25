#!/usr/bin/env python3
"""
Train LightGBM model for risk scoring
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import json
import os
import joblib
from pathlib import Path

def load_and_prepare_data(data_path: str):
    """Load and prepare training data"""
    # Load data
    df = pd.read_csv(data_path)
    
    # Define feature columns
    feature_columns = [
        'amount', 'hour_of_day', 'is_cross_border', 'merchant_risk_tier',
        'velocity_1h', 'amount_vs_user_avg', 'account_age_days',
        'failed_auth_count', 'device_seen_before', 'country_risk_score'
    ]
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['is_fraud']
    
    # Convert boolean columns to int
    bool_columns = ['is_cross_border', 'device_seen_before']
    for col in bool_columns:
        X[col] = X[col].astype(int)
    
    return X, y, feature_columns

def train_model(X_train, y_train, X_val, y_val, feature_columns):
    """Train LightGBM model"""
    # Create LightGBM datasets
    train_data = lgb.Dataset(X_train, label=y_train, feature_name=feature_columns)
    val_data = lgb.Dataset(X_val, label=y_val, feature_name=feature_columns, reference=train_data)
    
    # Model parameters
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'random_state': 42
    }
    
    # Train model
    print("Training LightGBM model...")
    model = lgb.train(
        params,
        train_data,
        valid_sets=[train_data, val_data],
        num_boost_round=1000,
        callbacks=[
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=100)
        ]
    )
    
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    # Make predictions
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)
    
    # Convert probabilities to binary predictions
    y_pred_binary = (y_pred > 0.5).astype(int)
    
    # Calculate metrics
    auc_roc = roc_auc_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred_binary)
    recall = recall_score(y_test, y_pred_binary)
    f1 = f1_score(y_test, y_pred_binary)
    
    metrics = {
        'auc_roc': auc_roc,
        'precision': precision,
        'recall': recall,
        'f1_score': f1
    }
    
    print(f"Model Performance:")
    print(f"AUC-ROC: {auc_roc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")
    
    return metrics

def save_model(model, feature_columns, metrics, output_dir: str):
    """Save model and metadata"""
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'risk_lgbm.txt')
    model.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Save metadata
    metadata = {
        'model_type': 'LightGBM',
        'feature_columns': feature_columns,
        'metrics': metrics,
        'model_version': '1.0.0',
        'training_date': pd.Timestamp.now().isoformat()
    }
    
    metadata_path = os.path.join(output_dir, 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {metadata_path}")

def main():
    """Main training function"""
    # Paths
    data_path = "data/train.csv"
    output_dir = "model_artifacts"
    
    # Load and prepare data
    print("Loading and preparing data...")
    X, y, feature_columns = load_and_prepare_data(data_path)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Further split training for validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Validation set size: {len(X_val)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val, feature_columns)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Save model
    save_model(model, feature_columns, metrics, output_dir)
    
    print("Training complete!")

if __name__ == "__main__":
    main()