import time
from typing import List, Dict, Any
from .scorer import RiskScorer
from .rule_engine import RuleEngine
from .schemas import Transaction, TransactionResult

class RiskPipeline:
    def __init__(self):
        self.scorer = RiskScorer()
        self.rule_engine = RuleEngine()
        
    def process_batch(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Process a batch of transactions through ML + rule engine"""
        results = []
        
        for transaction in transactions:
            # Get ML score
            ml_score = self.scorer.score(transaction)
            
            # Apply rules
            rule_hits = self.rule_engine.evaluate(transaction, ml_score)
            
            # Make final decision
            decision, confidence = self._make_decision(ml_score, rule_hits)
            
            result = TransactionResult(
                transaction_id=transaction.transaction_id,
                ml_score=ml_score,
                rule_hits=rule_hits,
                final_decision=decision,
                confidence=confidence,
                processing_time_ms=0.0  # Will be updated by caller
            )
            results.append(result)
        
        # Calculate workload reduction
        auto_approved = sum(1 for r in results if r.final_decision == "AUTO_APPROVE")
        auto_rejected = sum(1 for r in results if r.final_decision == "AUTO_REJECT")
        manual_review = sum(1 for r in results if r.final_decision == "MANUAL_REVIEW")
        
        # Calculate workload reduction percentage
        # Manual workload is manual_review / total
        # Reduction is (1 - manual_review / total) * 100
        total = len(transactions)
        manual_percentage = (manual_review / total) * 100 if total > 0 else 0
        workload_reduction = 100 - manual_percentage
        
        return {
            "auto_approved": auto_approved,
            "manual_review": manual_review,
            "auto_rejected": auto_rejected,
            "workload_reduction_percent": round(workload_reduction, 1),
            "results": results
        }
    
    def _make_decision(self, ml_score: float, rule_hits: List[str]) -> tuple:
        """Make final decision based on ML score and rules"""
        # High confidence decisions
        if ml_score < 0.2 and not rule_hits:
            return "AUTO_APPROVE", 0.95
        elif ml_score > 0.8 or "HIGH_RISK_RULE" in rule_hits:
            return "AUTO_REJECT", 0.95
        
        # Medium confidence decisions
        if ml_score < 0.4 and len(rule_hits) <= 1:
            return "AUTO_APPROVE", 0.75
        elif ml_score > 0.7 or len(rule_hits) >= 2:
            return "AUTO_REJECT", 0.75
        
        # Low confidence - manual review
        return "MANUAL_REVIEW", 0.5