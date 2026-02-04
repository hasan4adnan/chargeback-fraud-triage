# Chargeback & Fraud Triage Platform

Local, explainable fraud triage system using KNN similarity scoring.

This project is designed as a practical decision-support tool: it scores a transaction, shows similar historical cases, and returns an operational triage decision.

## What It Does

- Scores transaction risk with KNN (`risk_score`)
- Returns explainability payload:
  - nearest historical case IDs
  - fraud ratio among neighbors
  - neighbor distances
  - human-readable rationale
- Applies triage policy:
  - `auto_approve`
  - `manual_review`
  - `auto_block`

## Architecture (Local Only)

- `api/` (Node.js): request validation + triage decision thresholds
- `ml_service/` (FastAPI): KNN inference + explainability
- `scripts/train_model.py`: trains artifacts from the prepared dataset

Flow:
1. Client/Postman calls `POST /score_transaction` on Node API (`:3000`)
2. Node API calls ML service `POST /score` (`:8001`)
3. ML service returns score + evidence
4. Node API returns final triage response

## Dataset Assumption

Dataset is already prepared and located at:

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

## Requirements

- Python 3.11+
- Node.js 20+

## Quickstart

From project root:

```bash
cd chargeback-fraud-triage
```

### 1) Install Python deps and train model artifacts

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

Health check:

```bash
curl http://localhost:8001/health
```

### 3) Start Node API (new terminal)

```bash
cd api
npm install
ML_SERVICE_URL=http://localhost:8001 npm start
```

Health check:

```bash
curl http://localhost:3000/health
```

## Postman Test

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
- `POST /score_transaction` (direct ML scoring with decision)

## Example Response

```json
{
  "transaction_id": "abc123",
  "risk_score": 0.8052,
  "confidence_band": "high",
  "decision": "auto_block",
  "nearest_neighbors": [8157, 4975],
  "fraud_ratio_neighbors": 0.8,
  "distances": [5.2152, 5.6265],
  "rationale": "This transaction is similar to 15 historical cases; 12 were confirmed fraud.",
  "thresholds": {
    "low_threshold": 0.35,
    "high_threshold": 0.75
  }
}
```

## Triage Thresholds

Node API thresholds are configurable via env vars:

- `LOW_THRESHOLD` (default: `0.35`)
- `HIGH_THRESHOLD` (default: `0.75`)

Example:

```bash
LOW_THRESHOLD=0.30 HIGH_THRESHOLD=0.70 ML_SERVICE_URL=http://localhost:8001 npm start
```

## Common Issues

- `Cannot GET /score_transaction`
  - Use `POST`, not `GET`.
- `Unexpected non-whitespace character after JSON`
  - JSON body has invalid syntax (usually trailing comma).
- `cd: no such file or directory: api`
  - You are not in `chargeback-fraud-triage/` root.

## Project Structure

```text
chargeback-fraud-triage/
├── README.md
├── api/
├── data/
├── docs/
├── ml_service/
├── models/
└── scripts/
```

## License

MIT (or your preferred license).
