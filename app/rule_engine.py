from typing import List, Dict, Any
from schemas import Transaction
from static_rules import RULE_DEFINITIONS, RULE_PRIORITY

class RuleEngine:
    def __init__(self):
        self.rules = RULE_DEFINITIONS
        self.priority = RULE_PRIORITY
        
    def evaluate(self, transaction: Transaction, ml_score: float) -> List[str]:
        """Evaluate transaction against all rules"""
        triggered_rules = []
        
        # Evaluate all rules
        for rule_name, rule_def in self.rules.items():
            if self._evaluate_rule(transaction, rule_def["condition"]):
                triggered_rules.append(rule_name)
        
        # Add ML-based rule
        if ml_score > 0.8:
            triggered_rules.append("HIGH_ML_SCORE")
        elif ml_score < 0.2:
            triggered_rules.append("LOW_ML_SCORE")
        
        return triggered_rules
    
    def _evaluate_rule(self, transaction: Transaction, condition: str) -> bool:
        """Evaluate a single rule condition"""
        try:
            # Create a local namespace with transaction attributes
            local_vars = {
                'amount': transaction.amount,
                'hour_of_day': transaction.hour_of_day,
                'is_cross_border': transaction.is_cross_border,
                'merchant_risk_tier': transaction.merchant_risk_tier,
                'velocity_1h': transaction.velocity_1h,
                'amount_vs_user_avg': transaction.amount_vs_user_avg,
                'account_age_days': transaction.account_age_days,
                'failed_auth_count': transaction.failed_auth_count,
                'device_seen_before': transaction.device_seen_before,
                'country_risk_score': transaction.country_risk_score
            }
            
            # Evaluate the condition
            return eval(condition, {"__builtins__": {}}, local_vars)
            
        except Exception as e:
            # If rule evaluation fails, default to False
            return False
    
    def get_rule_details(self, rule_name: str) -> Dict[str, Any]:
        """Get detailed information about a rule"""
        if rule_name == "HIGH_ML_SCORE":
            return {
                "name": "High ML Risk Score",
                "description": "ML model indicates high risk",
                "severity": "high",
                "action": "reject"
            }
        elif rule_name == "LOW_ML_SCORE":
            return {
                "name": "Low ML Risk Score",
                "description": "ML model indicates low risk",
                "severity": "low",
                "action": "approve"
            }
        else:
            return self.rules.get(rule_name, {})
    
    def get_triggered_rules_by_severity(self, triggered_rules: List[str]) -> Dict[str, List[str]]:
        """Group triggered rules by severity"""
        severity_groups = {"high": [], "medium": [], "low": []}
        
        for rule_name in triggered_rules:
            rule_details = self.get_rule_details(rule_name)
            if rule_details:
                severity = rule_details.get("severity", "low")
                if severity in severity_groups:
                    severity_groups[severity].append(rule_name)
        
        return severity_groups
    
    def get_final_action(self, triggered_rules: List[str]) -> str:
        """Determine final action based on triggered rules"""
        severity_groups = self.get_triggered_rules_by_severity(triggered_rules)
        
        # High severity rules trigger rejection
        if severity_groups["high"]:
            return "reject"
        
        # Medium severity rules trigger review
        if severity_groups["medium"]:
            return "review"
        
        # Low severity rules trigger flagging
        if severity_groups["low"]:
            return "flag"
        
        # No rules triggered
        return "pass"