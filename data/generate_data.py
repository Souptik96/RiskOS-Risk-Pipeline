#!/usr/bin/env python3
"""
Generate synthetic transaction data for risk pipeline testing and training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

class TransactionDataGenerator:
    def __init__(self, num_samples: int = 1000):
        self.num_samples = num_samples
        np.random.seed(42)
        
    def generate_transactions(self) -> List[Dict[str, Any]]:
        """Generate synthetic transaction data"""
        transactions = []
        
        for i in range(self.num_samples):
            # Generate base transaction
            transaction = {
                "transaction_id": f"txn_{i:06d}",
                "amount": self._generate_amount(),
                "hour_of_day": np.random.randint(0, 24),
                "is_cross_border": np.random.choice([True, False], p=[0.3, 0.7]),
                "merchant_risk_tier": np.random.randint(1, 6),
                "velocity_1h": np.random.randint(0, 15),
                "amount_vs_user_avg": np.random.uniform(0.1, 8.0),
                "account_age_days": np.random.randint(1, 1095),  # 1 day to 3 years
                "failed_auth_count": np.random.randint(0, 8),
                "device_seen_before": np.random.choice([True, False], p=[0.8, 0.2]),
                "country_risk_score": np.random.uniform(0.0, 1.0)
            }
            
            # Add some correlations to make data more realistic
            self._add_correlations(transaction)
            
            transactions.append(transaction)
        
        return transactions
    
    def _generate_amount(self) -> float:
        """Generate transaction amount with realistic distribution"""
        # Most transactions are small, few are large
        if np.random.random() < 0.8:
            # Small transactions ($10-$500)
            return np.random.uniform(10, 500)
        elif np.random.random() < 0.95:
            # Medium transactions ($500-$5000)
            return np.random.uniform(500, 5000)
        else:
            # Large transactions ($5000-$50000)
            return np.random.uniform(5000, 50000)
    
    def _add_correlations(self, transaction: Dict[str, Any]):
        """Add realistic correlations between features"""
        # High amount transactions more likely to be cross-border
        if transaction["amount"] > 5000:
            transaction["is_cross_border"] = np.random.choice([True, False], p=[0.7, 0.3])
        
        # New accounts more likely to have failed auth
        if transaction["account_age_days"] < 30:
            transaction["failed_auth_count"] = min(transaction["failed_auth_count"] + 1, 8)
        
        # High velocity more likely with new devices
        if not transaction["device_seen_before"] and transaction["velocity_1h"] < 5:
            transaction["velocity_1h"] += np.random.randint(0, 5)
        
        # Cross-border transactions have higher country risk
        if transaction["is_cross_border"]:
            transaction["country_risk_score"] = max(transaction["country_risk_score"], np.random.uniform(0.3, 1.0))
    
    def generate_csv(self, output_path: str):
        """Generate CSV file with transaction data"""
        transactions = self.generate_transactions()
        df = pd.DataFrame(transactions)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"Generated {len(transactions)} transactions to {output_path}")
    
    def generate_training_data(self, output_path: str):
        """Generate training data with labels"""
        transactions = self.generate_transactions()
        
        # Generate labels based on simple rules (in real scenario, these would be actual labels)
        labeled_data = []
        for tx in transactions:
            # Simple rule-based labeling for demonstration
            risk_score = 0.0
            
            # High amount increases risk
            if tx["amount"] > 10000:
                risk_score += 0.3
            elif tx["amount"] > 5000:
                risk_score += 0.15
            
            # Cross-border increases risk
            if tx["is_cross_border"]:
                risk_score += 0.2
            
            # High velocity increases risk
            if tx["velocity_1h"] > 10:
                risk_score += 0.25
            elif tx["velocity_1h"] > 5:
                risk_score += 0.1
            
            # Failed auth increases risk
            if tx["failed_auth_count"] > 3:
                risk_score += 0.3
            elif tx["failed_auth_count"] > 1:
                risk_score += 0.1
            
            # New device increases risk
            if not tx["device_seen_before"]:
                risk_score += 0.15
            
            # High country risk increases risk
            if tx["country_risk_score"] > 0.8:
                risk_score += 0.2
            elif tx["country_risk_score"] > 0.5:
                risk_score += 0.1
            
            # New account increases risk
            if tx["account_age_days"] < 30:
                risk_score += 0.15
            
            # Normalize risk score
            risk_score = min(risk_score, 1.0)
            
            # Convert to binary label (0 = low risk, 1 = high risk)
            label = 1 if risk_score > 0.5 else 0
            
            labeled_data.append({
                **tx,
                "risk_score": risk_score,
                "is_fraud": label
            })
        
        # Save to CSV
        df = pd.DataFrame(labeled_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Generated {len(labeled_data)} labeled transactions to {output_path}")

def main():
    """Main function to generate sample data"""
    generator = TransactionDataGenerator(num_samples=1000)
    
    # Generate sample CSV for testing
    generator.generate_csv("data/test.csv")
    
    # Generate training data
    generator.generate_training_data("data/train.csv")
    
    # Generate a small batch for API testing
    small_generator = TransactionDataGenerator(num_samples=10)
    small_transactions = small_generator.generate_transactions()
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_types(i) for i in obj]
        return obj

    serializable_transactions = convert_types(small_transactions)

    # Save as JSON for API testing
    with open("data/sample_batch.json", "w") as f:
        json.dump({"batch_id": "test_batch_001", "transactions": serializable_transactions}, f, indent=2)
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    main()