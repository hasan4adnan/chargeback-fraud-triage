# Architecture (Local)

## Services

- **Node.js API (control plane)**
  - Validates request payload
  - Applies triage thresholds
  - Returns investigator-friendly response
- **Python ML service (data plane)**
  - Loads trained artifacts from `models/`
  - Runs KNN similarity scoring
  - Returns explainability fields (neighbors, distances, fraud ratio)

## Request flow

1. Postman/client sends `POST /score_transaction` to Node API (`localhost:3000`).
2. Node API forwards data to ML service (`localhost:8001/score`).
3. ML service returns risk and explanation.
4. Node API adds decision (`auto_approve`, `manual_review`, `auto_block`) and returns final payload.
