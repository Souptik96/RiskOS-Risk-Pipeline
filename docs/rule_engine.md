# Rule Engine Documentation

The RiskOS Risk Pipeline utilizes a hybrid approach to transaction triage, combining Machine Learning (ML) inference with a deterministic Rule Engine.

## 1. How Rules are Evaluated

The Rule Engine evaluates transactions in a **sequential, first-match-priority** manner within severity tiers.
-   **Execution Order**: Rules are grouped by severity (High, Medium, Low).
-   **Priority**: High severity rules are checked first. If a High severity rule is triggered, the transaction is immediately slated for escalation (AUTO_REJECT in terms of automaticity, ESCALATE in terms of human triage).
-   **State Management**: Rules are stateless and rely entirely on the transaction payload and the calculated ML score.

## 2. Triage Decisions (ML + Rule Logic)

Decisions are made following this logic flow:
1.  **ML Inference**: The LightGBM model calculates a risk score (0.0 to 1.0).
2.  **Rule Mapping**: The transaction is passed through the 15 static rules.
3.  **Conflict Resolution**:
    -   If a **High Risk Rule** fires OR the **ML Score > 0.8**, the decision is `ESCALATE`.
    -   If **No Rules** fire AND the **ML Score < 0.2**, the decision is `AUTO_CLOSE`.
    -   If **Medium Risk Rules** fire OR the **ML Score is between 0.45 and 0.8**, the decision is `ESCALATE` (to the human review queue).
    -   If only **Low Risk Rules** fire, the decision is `MONITOR`.

## 3. How to Add a New Rule

To add a new rule, follow these steps:

1.  **Define the Rule**: Open `app/static_rules.py`.
2.  **Add to `RULE_DEFINITIONS`**:
    ```python
    "NEW_RULE_ID": {
        "name": "Human Readable Name",
        "description": "Short description of the logic",
        "condition": "velocity_1h > 15", # Python expression
        "severity": "high", # high, medium, or low
        "action": "reject" # reject, review, or flag
    }
    ```
3.  **Update Priority**: Add the ID to the appropriate list in `RULE_PRIORITY`.
4.  **Test**: Run `pytest tests/test_pipeline.py` to ensure the new rule integrates correctly.

## 4. GPT Rule Refinement

The `/api/v1/rules/refine` endpoint optionally leverages LLMs (GPT-4o-mini) to:
-   Analyze batches of false positives.
-   Identify patterns that static rules missed.
-   Suggest threshold adjustments (e.g., changing `velocity_1h > 10` to `velocity_1h > 12`).
-   **Audit Trail**: All GPT suggestions must be manually approved via the UI before being committed to `static_rules.py`.

## 5. Why Static Rules + ML?

We use this hybrid "Human-in-the-loop" architecture for several reasons:
-   **Explainability**: While ML scores can be opaque, a rule hit like `High Velocity` gives analysts immediate context.
-   **Regulatory Compliance**: Many jurisdictions require specific deterministic checks (e.g., OFAC sanctions) that cannot be left solely to probabilistic models.
-   **Agility**: In a "flash fraud" event, developers can deploy a new static rule in minutes, while retraining an ML model takes significantly longer.
-   **Edge Case Handling**: ML models sometimes fail on extreme outliers; static rules provide a safety net for "Zero Day" fraud patterns.