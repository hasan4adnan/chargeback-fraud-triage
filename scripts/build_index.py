#!/usr/bin/env python3
from __future__ import annotations

import argparse
import joblib

from sklearn.neighbors import NearestNeighbors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Rebuild nearest-neighbor index from saved classifier')
    parser.add_argument('--scaled-matrix', required=True, help='Path to saved scaled feature matrix .joblib')
    parser.add_argument('--neighbors', type=int, default=15, help='Number of neighbors')
    parser.add_argument('--output', default='models/nn_index.joblib', help='Output index path')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    X_scaled = joblib.load(args.scaled_matrix)
    index = NearestNeighbors(n_neighbors=args.neighbors, metric='euclidean')
    index.fit(X_scaled)
    joblib.dump(index, args.output)
    print(f'Index saved to {args.output}')


if __name__ == '__main__':
    main()
