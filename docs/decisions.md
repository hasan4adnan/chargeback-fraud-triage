# Decision Log

## D1: KNN as core model

- Chosen for explainability by analogy.
- Supports investigator workflow: "show similar historical cases".

## D2: No extra feature engineering in this implementation

- Dataset already contains model-ready columns.
- Service only enforces column order and numeric typing.

## D3: Local-first runtime

- System runs fully on local machine.
- No cloud infrastructure required.

## D4: Config-driven triage thresholds

- `LOW_THRESHOLD` and `HIGH_THRESHOLD` env vars in API.
- Enables decision tuning without retraining.
