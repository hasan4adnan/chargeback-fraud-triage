#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.preprocessing import StandardScaler

TARGET_COL = 'CBK'
DROP_COLS = ['Unnamed: 0', 'Card Number', 'Date']


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Train fraud KNN artifacts')
    parser.add_argument('--input', required=True, help='Input CSV path')
    parser.add_argument('--output-dir', default='models', help='Artifacts output directory')
    parser.add_argument('--neighbors', type=int, default=15, help='Number of neighbors')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    if TARGET_COL not in df.columns:
        raise ValueError(f"Missing target column '{TARGET_COL}'")

    feature_columns = [
        col
        for col in df.columns
        if col not in DROP_COLS + [TARGET_COL]
    ]

    X = df[feature_columns].astype(float)
    y = (df[TARGET_COL].str.lower() == 'yes').astype(int)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    classifier = KNeighborsClassifier(n_neighbors=args.neighbors, weights='distance')
    classifier.fit(X_scaled, y)

    index = NearestNeighbors(n_neighbors=args.neighbors, metric='euclidean')
    index.fit(X_scaled)

    reference = {
        'row_ids': df['Unnamed: 0'].astype(int).tolist(),
        'labels': y.astype(int).tolist(),
    }

    # Lightweight runtime artifact for fast local inference.
    np.savez_compressed(
        output_dir / 'runtime_bundle.npz',
        X_scaled=X_scaled.astype(np.float32),
        labels=y.to_numpy(dtype=np.int8),
        row_ids=df['Unnamed: 0'].to_numpy(dtype=np.int64),
        mean=scaler.mean_.astype(np.float32),
        scale=scaler.scale_.astype(np.float32),
    )
    with open(output_dir / 'runtime_bundle.json', 'w', encoding='utf-8') as f:
        json.dump(
            {
                'X_scaled': X_scaled.astype(float).tolist(),
                'labels': y.astype(int).tolist(),
                'row_ids': df['Unnamed: 0'].astype(int).tolist(),
                'mean': scaler.mean_.astype(float).tolist(),
                'scale': scaler.scale_.astype(float).tolist(),
            },
            f,
        )

    metadata = {
        'feature_columns': feature_columns,
        'n_neighbors': args.neighbors,
        'dataset': str(input_path),
        'target_column': TARGET_COL,
    }

    joblib.dump(scaler, output_dir / 'scaler.joblib')
    joblib.dump(classifier, output_dir / 'knn_classifier.joblib')
    joblib.dump(index, output_dir / 'nn_index.joblib')
    joblib.dump(reference, output_dir / 'reference.joblib')
    joblib.dump(X_scaled, output_dir / 'scaled_matrix.joblib')
    with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f'Trained artifacts saved in {output_dir}')
    print(f'Features used: {feature_columns}')


if __name__ == '__main__':
    main()
