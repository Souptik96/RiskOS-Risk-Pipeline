# ⚡ RiskOS Risk Pipeline

> Automated transaction triage engine combining ML scoring and rule-based
> decision-making to reduce manual fraud review workload by ~70%.

![HF Space](https://img.shields.io/badge/🤗%20HuggingFace-Live%20Demo-yellow?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**Live API:** https://soupstick-risk-pipeline.hf.space
**API Docs:** https://soupstick-risk-pipeline.hf.space/docs

---

### The Problem This Solves

Manual fraud review today is a slow, expensive bottleneck where analysts must hand-check thousands of low-risk transactions every day. This repetitive process increases operational costs and delays legitimate customer payments, leading to a poor user experience. The RiskOS Risk Pipeline automates this triage by using ML-driven scoring and safety rules to instantly approve or flag transactions, reducing the manual review workload by approximately 70%.

---

### How It Works

Incoming Transactions (batch, up to 500)
│
▼
**LightGBM Scorer**
├── Risk score: 0.0 – 1.0
└── Threshold: 0.45
│
▼
**Rule Engine (15 static rules)**
├── Velocity rules
├── Cross-border rules
├── Amount anomaly rules
└── Device + account age rules
│
▼
**Triage Decision**
├── `ESCALATE`  → Human analyst queue
├── `MONITOR`   → Watchlist + auto-flag
└── `AUTO_CLOSE` → No human needed
│
▼
**Output: Structured JSON**
├── per-transaction decision
├── rule that fired
├── workload_reduction_estimate
└── processing_time_ms

---

### Performance Metrics

| Metric | Value |
|---|---|
| Model | LightGBM |
| Recall | 0.89 |
| Precision | 0.87 |
| AUC-ROC | 0.92 |
| Decision threshold | 0.45 |
| Workload reduction | ~70% |
| Latency (100 txns) | <5000ms |
| Max batch size | 500 transactions |
| Static rules | 15 |

---

### API — 60 Second Start

```bash
# Run a batch of transactions
curl -X POST https://soupstick-risk-pipeline.hf.space/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {
        "transaction_id": "txn-001",
        "amount": 9500,
        "hour_of_day": 3,
        "is_cross_border": true,
        "merchant_risk_tier": 3,
        "velocity_1h": 8,
        "amount_vs_user_avg": 4.5,
        "account_age_days": 15,
        "failed_auth_count": 2,
        "device_seen_before": false,
        "country_risk_score": 0.85
      }
    ]
  }'

# Get active rules
curl https://soupstick-risk-pipeline.hf.space/api/v1/rules

# Refine rules using false positives (requires LLM_API_KEY)
curl -X POST https://soupstick-risk-pipeline.hf.space/api/v1/rules/refine \
  -H "Content-Type: application/json" \
  -d '{"false_positives": [...]}'
```

---

### Local Development

```bash
git clone https://github.com/Souptik96/riskos-risk-pipeline
cd riskos-risk-pipeline
pip install -r requirements.txt
python data/generate_data.py        # generates train.csv and test.csv
python scripts/train_model.py       # trains LightGBM, asserts metrics, saves model
uvicorn app.main:app --port 7860    # starts API

# Or with Docker:
docker build -t riskos-risk-pipeline .
docker run -p 7860:7860 riskos-risk-pipeline
```

---

### Rule Engine

| Rule ID | Name | Condition | Action | Confidence |
|---|---|---|---|---|
| R001 | High Amount | amount > 10000 | ESCALATE | 0.95 |
| R002 | High Velocity | velocity_1h > 10 | ESCALATE | 0.95 |
| R003 | High Risk Country | country_risk_score > 0.8 | ESCALATE | 0.95 |
| R004 | Failed Auth | failed_auth_count > 3 | ESCALATE | 0.95 |
| R005 | Medium Amount | 5000 < amount <= 10000 | ESCALATE | 0.85 |
| R006 | Cross-Border | is_cross_border == True | ESCALATE | 0.80 |
| R007 | New Device | device_seen_before == False | ESCALATE | 0.75 |
| R008 | High Risk Merchant | merchant_risk_tier >= 4 | ESCALATE | 0.85 |
| R009 | Unusual Hour | hour_of_day < 6 or > 22 | ESCALATE | 0.70 |
| R010 | Amount Anomaly | amount_vs_user_avg > 3.0 | MONITOR | 0.65 |
| R011 | New Account | account_age_days < 30 | MONITOR | 0.60 |
| R012 | Medium Velocity | 5 < velocity_1h <= 10 | MONITOR | 0.70 |
| R013 | Medium Risk Merchant | merchant_risk_tier == 3 | MONITOR | 0.65 |
| R014 | Medium Risk Country | 0.5 < country_risk_score <= 0.8 | MONITOR | 0.60 |
| R015 | High ML Score | ml_score > 0.8 | ESCALATE | 0.92 |

---

### Test Results
Test Results (last run: 2026-03-25)
- `test_pipeline.py`: 7 passed / 0 failed
- `test_api.py`: 9 passed / 0 failed
- **Total: 16/16 passed**

---

### Optional — GPT Rule Refinement

If `LLM_API_KEY` is set (OpenAI), the `/api/v1/rules/refine` endpoint uses GPT-4o-mini to suggest rule modifications based on recent false positives. Without the key, the endpoint returns current static rules unchanged.

Add `LLM_API_KEY` to your environment or HuggingFace Secrets to enable this.

---

### Part of RiskOS

| Repository | Description | Link |
|---|---|---|
| **RiskOS** | Core Orchestrator & Multi-Agent Switchboard | [Link](https://github.com/Souptik96/RiskOS) |
| **Risk-Pipeline** | ML Triage & Rule Engine (this repo) | [Link](https://github.com/Souptik96/RiskOS-Risk-Pipeline) |
| **LLM-Guard** | RAG-Augmented Guardrails | [Link](https://github.com/Souptik96/RiskOS-LLM-Guard) |
| **Marketplace-Intelligence** | NL→SQL Analytics Layer | [Link](https://github.com/Souptik96/RiskOS-Marketplace-Intelligence) |