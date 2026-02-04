from .knn_model import FraudKNNModel


class InferenceService:
    def __init__(self, model_dir: str = 'models') -> None:
        self.model = FraudKNNModel(model_dir=model_dir)

    def score_transaction(self, payload: dict) -> dict:
        return self.model.score(payload)
