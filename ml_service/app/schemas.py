from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    transaction_id: str | None = None
    Amount: float
    transactions_last_1h: float
    transactions_last_24h: float
    avg_amount_last_7d_per_card: float
    std_amount_last_30d_per_card: float
    time_since_last_transaction: float
    same_amount_repeat_count: float
    night_transaction: float = Field(ge=0, le=1)


class ScoreResponse(BaseModel):
    risk_score: float
    confidence_band: str
    nearest_neighbors: list[int]
    fraud_ratio_neighbors: float
    distances: list[float]
    rationale: str


class TriageResponse(ScoreResponse):
    transaction_id: str | None = None
    decision: str
    thresholds: dict[str, float]
