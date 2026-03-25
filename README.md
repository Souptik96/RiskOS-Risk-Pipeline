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

## 🛑 The Problem This Solves

Manual fraud review today is a slow, expensive bottleneck where analysts must hand-check thousands of low-risk transactions every day. This repetitive process increases operational costs and delays legitimate customer payments, leading to a poor user experience. The RiskOS Risk Pipeline automates this triage by using ML-driven scoring and safety rules to instantly approve or flag transactions, reducing the manual review workload by approximately 70%.

---

## ⚙️ How It Works

1.  **Data Ingestion**: The pipeline receives real-time transaction data (amount, location, velocity, user history) via a high-performance FastAPI interface.
2.  **ML Scoring**: A LightGBM model calculates a risk probability (0.0 to 1.0) based on trained features such as country risk scores and anomalous spending patterns.
3.  **Rule Engine**: Parallel to the ML inference, a flexible rule engine applies static business rules (e.g., specific high-risk jurisdictions or velocity thresholds) to ensure deterministic compliance.
4.  **Automated Triage**: Results are combined to produce a final verdict—`PASS`, `REVIEW`, or `FLAG`—allowing analysts to focus only on the most complex edge cases.

---

## 📁 Repository Structure

```
riskos-risk-pipeline/
├── README.md
├── LICENSE                    (MIT)
├── .gitignore
├── .env.example
├── requirements.txt
├── Dockerfile
│
├── app/
│   ├── main.py
│   ├── pipeline.py
│   ├── scorer.py
│   ├── rule_engine.py
│   ├── static_rules.py
│   └── schemas.py
│
├── model_artifacts/
│   ├── risk_lgbm.txt
│   └── metadata.json
│
├── data/
│   ├── generate_data.py
│   ├── train.csv
│   └── test.csv
│
├── scripts/
│   └── train_model.py
│
├── tests/
│   ├── fixtures/
│   │   └── sample_batch.json
│   ├── test_pipeline.py
│   └── test_api.py
│
└── docs/
    └── rule_engine.md
```