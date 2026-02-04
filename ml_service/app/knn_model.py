from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .feature_engineering import build_feature_vector


class FraudKNNModel:
    def __init__(self, model_dir: str = 'models') -> None:
        self.model_dir = Path(model_dir)
        with open(self.model_dir / 'metadata.json', 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        runtime = np.load(self.model_dir / 'runtime_bundle.npz')
        self.X_scaled = runtime['X_scaled']
        self.labels = runtime['labels']
        self.row_ids = runtime['row_ids']
        self.mean = runtime['mean']
        self.scale = runtime['scale']

        self.feature_columns: list[str] = self.metadata['feature_columns']

    def score(self, payload: dict) -> dict:
        vector = build_feature_vector(payload, self.feature_columns)
        scaled = (vector - self.mean) / np.where(self.scale == 0, 1.0, self.scale)

        diffs = self.X_scaled - scaled.astype(np.float32)
        all_distances = np.linalg.norm(diffs, axis=1)
        k = min(int(self.metadata['n_neighbors']), len(all_distances))
        idx = np.argpartition(all_distances, k - 1)[:k]
        idx = idx[np.argsort(all_distances[idx])]
        dists = all_distances[idx]
        neighbor_ids = [int(self.row_ids[i]) for i in idx]
        neighbor_labels = [int(self.labels[i]) for i in idx]

        weights = 1.0 / (dists + 1e-6)
        fraud_prob = float(np.sum(weights * np.array(neighbor_labels)) / np.sum(weights))
        fraud_ratio = float(np.mean(neighbor_labels))

        if fraud_prob >= 0.75:
            confidence = 'high'
        elif fraud_prob >= 0.45:
            confidence = 'medium'
        else:
            confidence = 'low'

        rationale = (
            f"This transaction is similar to {len(neighbor_ids)} historical cases; "
            f"{sum(neighbor_labels)} were confirmed fraud."
        )

        return {
            'risk_score': round(fraud_prob, 4),
            'confidence_band': confidence,
            'nearest_neighbors': neighbor_ids,
            'fraud_ratio_neighbors': round(fraud_ratio, 4),
            'distances': [round(float(x), 4) for x in dists],
            'rationale': rationale,
        }
