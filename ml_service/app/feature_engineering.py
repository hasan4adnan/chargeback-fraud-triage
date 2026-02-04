import numpy as np


def build_feature_vector(payload: dict, feature_columns: list[str]) -> np.ndarray:
    # Dataset already contains model-ready columns; only enforce order/type.
    values = [float(payload[col]) for col in feature_columns]
    return np.array(values, dtype=float).reshape(1, -1)
