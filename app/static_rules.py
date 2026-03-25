# Static rule definitions for risk pipeline

RULE_DEFINITIONS = {
    # High Risk Rules (immediate rejection)
    "HIGH_AMOUNT": {
        "name": "High Amount Transaction",
        "description": "Transaction amount exceeds threshold",
        "condition": "amount > 10000",
        "severity": "high",
        "action": "reject"
    },
    "HIGH_VELOCITY": {
        "name": "High Transaction Velocity",
        "description": "Too many transactions in short time",
        "condition": "velocity_1h > 10",
        "severity": "high",
        "action": "reject"
    },
    "HIGH_RISK_COUNTRY": {
        "name": "High Risk Country",
        "description": "Transaction from high-risk country",
        "condition": "country_risk_score > 0.8",
        "severity": "high",
        "action": "reject"
    },
    "FAILED_AUTH": {
        "name": "Multiple Failed Authentications",
        "description": "Multiple authentication failures",
        "condition": "failed_auth_count > 3",
        "severity": "high",
        "action": "reject"
    },
    
    # Medium Risk Rules (review required)
    "MEDIUM_AMOUNT": {
        "name": "Medium Amount Transaction",
        "description": "Transaction amount in medium range",
        "condition": "amount > 5000 and amount <= 10000",
        "severity": "medium",
        "action": "review"
    },
    "CROSS_BORDER": {
        "name": "Cross-Border Transaction",
        "description": "Transaction crosses international borders",
        "condition": "is_cross_border == True",
        "severity": "medium",
        "action": "review"
    },
    "NEW_DEVICE": {
        "name": "New Device",
        "description": "Transaction from previously unseen device",
        "condition": "device_seen_before == False",
        "severity": "medium",
        "action": "review"
    },
    "HIGH_MERCHANT_RISK": {
        "name": "High Risk Merchant",
        "description": "Transaction with high-risk merchant",
        "condition": "merchant_risk_tier >= 4",
        "severity": "medium",
        "action": "review"
    },
    "UNUSUAL_HOUR": {
        "name": "Unusual Transaction Hour",
        "description": "Transaction during unusual hours",
        "condition": "hour_of_day < 6 or hour_of_day > 22",
        "severity": "medium",
        "action": "review"
    },
    
    # Low Risk Rules (consideration only)
    "AMOUNT_ANOMALY": {
        "name": "Amount Anomaly",
        "description": "Transaction amount significantly higher than user average",
        "condition": "amount_vs_user_avg > 3.0",
        "severity": "low",
        "action": "flag"
    },
    "NEW_ACCOUNT": {
        "name": "New Account",
        "description": "Transaction from newly created account",
        "condition": "account_age_days < 30",
        "severity": "low",
        "action": "flag"
    },
    "MEDIUM_VELOCITY": {
        "name": "Medium Transaction Velocity",
        "description": "Moderate transaction frequency",
        "condition": "velocity_1h > 5 and velocity_1h <= 10",
        "severity": "low",
        "action": "flag"
    },
    "MEDIUM_MERCHANT_RISK": {
        "name": "Medium Risk Merchant",
        "description": "Transaction with medium-risk merchant",
        "condition": "merchant_risk_tier == 3",
        "severity": "low",
        "action": "flag"
    },
    "MEDIUM_COUNTRY_RISK": {
        "name": "Medium Risk Country",
        "description": "Transaction from medium-risk country",
        "condition": "country_risk_score > 0.5 and country_risk_score <= 0.8",
        "severity": "low",
        "action": "flag"
    }
}

# Rule priority (for conflicting rules)
RULE_PRIORITY = {
    "high": ["HIGH_AMOUNT", "HIGH_VELOCITY", "HIGH_RISK_COUNTRY", "FAILED_AUTH"],
    "medium": ["MEDIUM_AMOUNT", "CROSS_BORDER", "NEW_DEVICE", "HIGH_MERCHANT_RISK", "UNUSUAL_HOUR"],
    "low": ["AMOUNT_ANOMALY", "NEW_ACCOUNT", "MEDIUM_VELOCITY", "MEDIUM_MERCHANT_RISK", "MEDIUM_COUNTRY_RISK"]
}