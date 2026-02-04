# Chargeback & Fraud Triage Platform

<img width="2752" height="1536" alt="chargeback-fraud-triage " src="https://github.com/user-attachments/assets/77df53d5-46b0-4fcf-b511-24c4bf3e8538" />


Local-first, explainable fraud triage platform built with Node.js + FastAPI and KNN similarity scoring.

It is designed for analyst workflows where decisions must be fast and interpretable: each score is backed by similar historical cases, neighbor fraud ratio, and distance evidence.

## Business Problem This Solves

Fraud and chargeback handling is not only an ML problem, it is an operations problem.

Fraud teams face high transaction volume, limited manual review capacity, and high costs from both:

- false negatives (missed fraud and chargeback losses)
- false positives (blocking legitimate users and hurting revenue/trust)

This project helps teams:

- prioritize which transactions to review first
- understand why a transaction is suspicious using similar historical cases
- apply consistent triage decisions (`auto_approve`, `manual_review`, `auto_block`)

The result is faster investigations, clearer analyst decisions, and better auditability.

## Core Capabilities

- Transaction risk scoring with KNN (`risk_score`)
- Explainability payload:
  - nearest historical case IDs
  - fraud ratio among neighbors
  - distance list
  - rationale string
- Operational triage decisions:
  - `auto_approve`
  - `manual_review`
  - `auto_block`
- Configurable thresholds via environment variables

## Local Architecture

- `api/` (Node.js control plane)
  - validates request payload
  - applies decision thresholds
  - exposes stable API contract
- `ml_service/` (FastAPI inference plane)
  - loads trained artifacts from `models/`
  - runs KNN inference and neighbor search
  - returns explainability fields

### Request Flow

1. Client calls `POST /score_transaction` on Node API (`localhost:3000`).
2. Node forwards payload to ML service (`localhost:8001/score`).
3. ML service computes score + evidence.
4. Node applies thresholds and returns final decision payload.

## Dataset

Prepared dataset path:

- `data/sample_transactions.csv`

Expected columns:

- `Unnamed: 0`
- `Card Number`
- `Date`
- `Amount`
- `CBK`
- `transactions_last_1h`
- `transactions_last_24h`
- `avg_amount_last_7d_per_card`
- `std_amount_last_30d_per_card`
- `time_since_last_transaction`
- `same_amount_repeat_count`
- `night_transaction`

Notes:
- `CBK` is the target (`Yes`/`No`).
- No additional feature engineering is required in this version.

## Requirements

- Python 3.11+
- Node.js 20+

## Quickstart

From project root:

```bash
cd chargeback-fraud-triage
```

### 1) Install Python dependencies and train artifacts

Option A (venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ml_service/requirements.txt
python scripts/train_model.py --input data/sample_transactions.csv --output-dir models --neighbors 15
```

Option B (conda):

```bash
conda activate ds
conda install -c conda-forge pandas scikit-learn joblib numpy fastapi uvicorn pydantic -y
python scripts/train_model.py --input data/sample_transactions.csv --output-dir models --neighbors 15
```

### 2) Start ML service

```bash
uvicorn ml_service.app.main:app --host 0.0.0.0 --port 8001
```

Health:

```bash
curl http://localhost:8001/health
```

### 3) Start Node API (new terminal)

```bash
cd api
npm install
ML_SERVICE_URL=http://localhost:8001 npm start
```

Health:

```bash
curl http://localhost:3000/health
```

## Postman Test (Recommended)

- Method: `POST`
- URL: `http://localhost:3000/score_transaction`
- Header: `Content-Type: application/json`
- Body (raw JSON):

```json
{
  "transaction_id": "abc123",
  "Amount": 250.75,
  "transactions_last_1h": 3,
  "transactions_last_24h": 8,
  "avg_amount_last_7d_per_card": 185.0,
  "std_amount_last_30d_per_card": 55.5,
  "time_since_last_transaction": 1200,
  "same_amount_repeat_count": 1,
  "night_transaction": 1
}
```

## API Endpoints

Node API (`http://localhost:3000`):

- `GET /health`
- `POST /score_transaction`

ML service (`http://localhost:8001`):

- `GET /health`
- `POST /score`
- `POST /score_transaction` (direct scoring path)

## Response Shape (Node API)

```json
{
  "transaction_id": "abc123",
  "risk_score": 0.8052,
  "confidence_band": "high",
  "decision": "auto_block",
  "nearest_neighbors": [8157, 4975, 4974],
  "fraud_ratio_neighbors": 0.8,
  "distances": [5.2152, 5.6265, 5.8364],
  "rationale": "This transaction is similar to 15 historical cases; 12 were confirmed fraud.",
  "thresholds": {
    "low_threshold": 0.35,
    "high_threshold": 0.75
  }
}
```

## Decision Thresholds

Configured in Node API:

- `LOW_THRESHOLD` (default: `0.35`)
- `HIGH_THRESHOLD` (default: `0.75`)

Example:

```bash
LOW_THRESHOLD=0.30 HIGH_THRESHOLD=0.70 ML_SERVICE_URL=http://localhost:8001 npm start
```

## Model Artifacts

Generated in `models/` by `scripts/train_model.py`:

- `scaler.joblib`
- `knn_classifier.joblib`
- `nn_index.joblib`
- `reference.joblib`
- `scaled_matrix.joblib`
- `runtime_bundle.npz`
- `runtime_bundle.json`
- `metadata.json`

## Common Issues

- `Cannot GET /score_transaction`
  - Use `POST` method.
- `Unexpected non-whitespace character after JSON`
  - Fix JSON syntax (remove trailing comma).
- `cd: no such file or directory: api`
  - Ensure you are inside `chargeback-fraud-triage/` before `cd api`.
- `FileNotFoundError: models/scaler.joblib`
  - Run training script before starting ML service.

## Project Structure

```text
chargeback-fraud-triage/
├── README.md
├── .gitignore
├── api/
│   ├── package.json
│   ├── package-lock.json
│   └── src/
│       ├── app.js
│       ├── routes/
│       │   └── scoreRoutes.js
│       ├── controllers/
│       │   └── scoreController.js
│       └── services/
│           └── mlClient.js
├── ml_service/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       ├── inference.py
│       ├── knn_model.py
│       └── feature_engineering.py
├── scripts/
│   ├── train_model.py
│   └── build_index.py
├── data/
│   ├── sample_transactions.csv
│   └── Chargeack_Frauds.csv
├── models/
│   ├── scaler.joblib
│   ├── knn_classifier.joblib
│   ├── nn_index.joblib
│   ├── reference.joblib
│   ├── scaled_matrix.joblib
│   ├── runtime_bundle.npz
│   ├── runtime_bundle.json
│   └── metadata.json
└── docs/
    ├── architecture.md
    ├── cost_analysis.md
    └── decisions.md
```

## License

MIT 
