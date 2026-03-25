# Risk Pipeline Rule Engine Documentation

## Overview

The Risk Pipeline Rule Engine is a sophisticated decision-making system that combines machine learning predictions with business rules to provide automated transaction risk assessment. It processes transactions through a 15-rule engine that evaluates various risk factors and produces final decisions: AUTO_APPROVE, MANUAL_REVIEW, or AUTO_REJECT.

## Architecture

The rule engine consists of three main components:

1. **Static Rules** (`static_rules.py`): Pre-defined business rules categorized by severity
2. **Rule Engine** (`rule_engine.py`): Core evaluation logic that applies rules to transactions
3. **ML Integration**: Combines rule-based decisions with LightGBM model predictions

## Rule Categories

### High Risk Rules (Immediate Rejection)

These rules trigger immediate transaction rejection due to clear high-risk indicators:

| Rule | Condition | Description |
|------|-----------|-------------|
| `HIGH_AMOUNT` | `amount > 10000` | Transaction amount exceeds $10,000 threshold |
| `HIGH_VELOCITY` | `velocity_1h > 10` | More than 10 transactions in the last hour |
| `HIGH_RISK_COUNTRY` | `country_risk_score > 0.8` | Transaction from high-risk country |
| `FAILED_AUTH` | `failed_auth_count > 3` | Multiple authentication failures |

### Medium Risk Rules (Manual Review)

These rules flag transactions for manual review due to moderate risk indicators:

| Rule | Condition | Description |
|------|-----------|-------------|
| `MEDIUM_AMOUNT` | `amount > 5000 and amount <= 10000` | Transaction amount between $5,000-$10,000 |
| `CROSS_BORDER` | `is_cross_border == True` | Transaction crosses international borders |
| `NEW_DEVICE` | `device_seen_before == False` | Transaction from previously unseen device |
| `HIGH_MERCHANT_RISK` | `merchant_risk_tier >= 4` | Transaction with high-risk merchant (tier 4-5) |
| `UNUSUAL_HOUR` | `hour_of_day < 6 or hour_of_day > 22` | Transaction during unusual hours (12am-6am or 10pm-12am) |

### Low Risk Rules (Flagging Only)

These rules provide additional context but don't automatically trigger rejection:

| Rule | Condition | Description |
|------|-----------|-------------|
| `AMOUNT_ANOMALY` | `amount_vs_user_avg > 3.0` | Transaction amount 3x+ user's average |
| `NEW_ACCOUNT` | `account_age_days < 30` | Transaction from account less than 30 days old |
| `MEDIUM_VELOCITY` | `velocity_1h > 5 and velocity_1h <= 10` | 6-10 transactions in the last hour |
| `MEDIUM_MERCHANT_RISK` | `merchant_risk_tier == 3` | Transaction with medium-risk merchant (tier 3) |
| `MEDIUM_COUNTRY_RISK` | `country_risk_score > 0.5 and country_risk_score <= 0.8` | Transaction from medium-risk country |

### ML-Based Rules

These rules are dynamically generated based on the LightGBM model predictions:

| Rule | Condition | Description |
|------|-----------|-------------|
| `HIGH_ML_SCORE` | `ml_score > 0.8` | ML model indicates high fraud probability (>80%) |
| `LOW_ML_SCORE` | `ml_score < 0.2` | ML model indicates low fraud probability (<20%) |

## Decision Logic

The rule engine combines ML predictions with rule evaluations to make final decisions:

### High Confidence Decisions

**AUTO_APPROVE** (95% confidence):
- ML score < 0.2 AND no rule hits

**AUTO_REJECT** (95% confidence):
- ML score > 0.8 OR any HIGH_RISK_RULE triggered

### Medium Confidence Decisions

**AUTO_APPROVE** (75% confidence):
- ML score < 0.4 AND ≤1 medium/low rule hits

**AUTO_REJECT** (75% confidence):
- ML score > 0.7 OR ≥2 rule hits

### Low Confidence Decisions

**MANUAL_REVIEW** (50% confidence):
- All other cases that don't meet high/medium confidence criteria

## Rule Priority System

When multiple rules are triggered, the system uses a priority hierarchy:

1. **High Priority**: High-risk rules take precedence
2. **Medium Priority**: Medium-risk rules considered next
3. **Low Priority**: Low-risk rules provide context

The final action is determined by the highest severity rule triggered:
- Any high-severity rule → REJECT
- Any medium-severity rule → REVIEW
- Only low-severity rules → FLAG
- No rules triggered → PASS

## Workload Reduction

The rule engine is designed to achieve approximately **70% workload reduction** by:

1. **Auto-approving** clearly safe transactions (low ML score + no rules)
2. **Auto-rejecting** clearly fraudulent transactions (high ML score + high-risk rules)
3. **Manual review** only for ambiguous cases

### Reduction Calculation

```
Workload Reduction % = (1 - Manual_Review_Count / Total_Transactions) × 100
```

Example:
- Total transactions: 1000
- Auto-approved: 600
- Auto-rejected: 100
- Manual review: 300
- Workload reduction: (1 - 300/1000) × 100 = 70%

## Implementation Details

### Rule Evaluation Process

1. **Feature Extraction**: Transaction data is extracted and normalized
2. **Rule Application**: Each rule condition is evaluated against transaction features
3. **ML Scoring**: LightGBM model generates risk probability
4. **Decision Making**: Rules and ML score combined using decision logic
5. **Result Generation**: Final decision with confidence score

### Error Handling

The rule engine includes robust error handling:
- Invalid rule conditions default to `False`
- Missing features use default values
- ML model failures trigger conservative (manual review) decisions
- All evaluations are logged for audit purposes

### Performance Optimizations

- **Vectorized Operations**: Batch processing for multiple transactions
- **Cached Rules**: Rule definitions loaded once at startup
- **Efficient ML Scoring**: LightGBM model optimized for fast inference
- **Parallel Processing**: Rules evaluated independently where possible

## Configuration

### Rule Thresholds

Key thresholds can be adjusted in `static_rules.py`:

```python
# Amount thresholds
HIGH_AMOUNT_THRESHOLD = 10000
MEDIUM_AMOUNT_THRESHOLD = 5000

# Velocity thresholds
HIGH_VELOCITY_THRESHOLD = 10
MEDIUM_VELOCITY_THRESHOLD = 5

# Risk score thresholds
HIGH_COUNTRY_RISK_THRESHOLD = 0.8
MEDIUM_COUNTRY_RISK_THRESHOLD = 0.5
```

### ML Integration Thresholds

ML score thresholds can be adjusted in `pipeline.py`:

```python
# High confidence thresholds
HIGH_ML_THRESHOLD = 0.8
LOW_ML_THRESHOLD = 0.2

# Medium confidence thresholds
MEDIUM_HIGH_ML_THRESHOLD = 0.7
MEDIUM_LOW_ML_THRESHOLD = 0.4
```

## Testing

The rule engine includes comprehensive tests:

- **Unit Tests**: Individual rule evaluation
- **Integration Tests**: End-to-end pipeline processing
- **Performance Tests**: Batch processing with 100+ transactions
- **Edge Case Tests**: Invalid data, empty batches, extreme values

Run tests with:
```bash
python -m pytest tests/test_pipeline.py
python -m pytest tests/test_api.py
```

## Monitoring and Logging

The rule engine provides detailed logging for:
- Rule trigger rates
- Decision distribution (approve/reject/review)
- ML score distributions
- Processing latency
- Error rates

Key metrics to monitor:
- **Workload Reduction %**: Target ~70%
- **Auto-approval Rate**: Should be >50%
- **Manual Review Rate**: Should be <30%
- **Rule Hit Rates**: Monitor individual rule effectiveness

## Future Enhancements

Planned improvements to the rule engine:

1. **Dynamic Rules**: Rules that adapt based on historical performance
2. **A/B Testing**: Test different rule configurations
3. **Explainable AI**: Detailed explanations for ML decisions
4. **Real-time Updates**: Hot-reload rule changes without restart
5. **Machine Learning**: Learn optimal rule thresholds from data
6. **Custom Rules**: User-defined rule builder interface

## Integration

The rule engine integrates with:

- **Fraud Intelligence Service**: Provides additional fraud signals
- **LLM Guard Service**: Can flag transactions for content review
- **Marketplace Intelligence**: Provides merchant and product context
- **External APIs**: Real-time identity verification, sanctions screening

## Security Considerations

- **Input Validation**: All transaction data validated before processing
- **Audit Logging**: Complete audit trail of all decisions
- **Rate Limiting**: Prevent abuse of the API endpoints
- **Data Privacy**: Sensitive data masked in logs
- **Access Control**: Role-based access to rule management

## Performance Benchmarks

Current performance metrics (on standard hardware):

- **Single Transaction**: <10ms processing time
- **Batch of 100**: <500ms processing time
- **Batch of 1000**: <2000ms processing time
- **Memory Usage**: <100MB for typical workloads
- **CPU Utilization**: <30% for continuous operation

## Troubleshooting

### Common Issues

1. **High Manual Review Rate**
   - Check if ML model needs retraining
   - Review rule thresholds for appropriateness
   - Analyze patterns in manual review cases

2. **Low Workload Reduction**
   - Increase confidence thresholds for auto-decisions
   - Add more high-precision rules
   - Improve ML model accuracy

3. **Slow Processing**
   - Check ML model loading time
   - Optimize rule evaluation logic
   - Consider batch processing for large volumes

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG_RULE_ENGINE=1
```

This provides detailed logging of:
- Rule evaluation results
- ML score calculations
- Decision-making process
- Performance metrics