from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., ge=0, description="Transaction amount")
    hour_of_day: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    is_cross_border: bool = Field(..., description="Is cross-border transaction")
    merchant_risk_tier: int = Field(..., ge=1, le=5, description="Merchant risk tier (1-5)")
    velocity_1h: int = Field(..., ge=0, description="Transaction count in last 1 hour")
    amount_vs_user_avg: float = Field(..., ge=0, description="Amount vs user average ratio")
    account_age_days: int = Field(..., ge=0, description="Account age in days")
    failed_auth_count: int = Field(..., ge=0, description="Failed authentication count")
    device_seen_before: bool = Field(..., description="Device seen before")
    country_risk_score: float = Field(..., ge=0, le=1, description="Country risk score (0-1)")

class PipelineRequest(BaseModel):
    batch_id: str = Field(..., description="Unique batch identifier")
    transactions: List[Transaction] = Field(..., description="List of transactions to process")

class TransactionResult(BaseModel):
    transaction_id: str
    ml_score: float = Field(..., ge=0, le=1, description="ML risk score (0-1)")
    rule_hits: List[str] = Field(default_factory=list, description="List of triggered rules")
    final_decision: str = Field(..., description="Final decision: AUTO_APPROVE, MANUAL_REVIEW, AUTO_REJECT")
    confidence: float = Field(..., ge=0, le=1, description="Decision confidence score")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

class PipelineResponse(BaseModel):
    batch_id: str
    total_transactions: int
    auto_approved: int
    manual_review: int
    auto_rejected: int
    workload_reduction_percent: float = Field(..., ge=0, le=100, description="Workload reduction percentage")
    processing_time_ms: float
    results: List[TransactionResult]
    timestamp: datetime = Field(default_factory=datetime.now)