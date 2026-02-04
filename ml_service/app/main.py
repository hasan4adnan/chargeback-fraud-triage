import os

from fastapi import FastAPI

from .inference import InferenceService
from .schemas import ScoreRequest, ScoreResponse, TriageResponse

app = FastAPI(title='Fraud KNN ML Service', version='1.0.0')
MODEL_DIR = os.getenv('MODEL_DIR', 'models')
LOW_THRESHOLD = float(os.getenv('LOW_THRESHOLD', '0.35'))
HIGH_THRESHOLD = float(os.getenv('HIGH_THRESHOLD', '0.75'))

inference = InferenceService(model_dir=MODEL_DIR)


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': 'fraud-knn-ml'}


@app.post('/score', response_model=ScoreResponse)
def score(payload: ScoreRequest) -> dict:
    return inference.score_transaction(payload.model_dump())


@app.post('/score_transaction', response_model=TriageResponse)
def score_transaction(payload: ScoreRequest) -> dict:
    scored = inference.score_transaction(payload.model_dump())
    risk = scored['risk_score']

    if risk >= HIGH_THRESHOLD:
        decision = 'auto_block'
    elif risk >= LOW_THRESHOLD:
        decision = 'manual_review'
    else:
        decision = 'auto_approve'

    return {
        'transaction_id': payload.transaction_id,
        **scored,
        'decision': decision,
        'thresholds': {
            'low_threshold': LOW_THRESHOLD,
            'high_threshold': HIGH_THRESHOLD,
        },
    }
