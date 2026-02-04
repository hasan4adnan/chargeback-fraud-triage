import { requestMlScore } from '../services/mlClient.js';

const REQUIRED_FIELDS = [
  'Amount',
  'transactions_last_1h',
  'transactions_last_24h',
  'avg_amount_last_7d_per_card',
  'std_amount_last_30d_per_card',
  'time_since_last_transaction',
  'same_amount_repeat_count',
  'night_transaction'
];

const LOW_THRESHOLD = Number(process.env.LOW_THRESHOLD ?? 0.35);
const HIGH_THRESHOLD = Number(process.env.HIGH_THRESHOLD ?? 0.75);

const decisionFromRisk = (riskScore) => {
  if (riskScore >= HIGH_THRESHOLD) return 'auto_block';
  if (riskScore >= LOW_THRESHOLD) return 'manual_review';
  return 'auto_approve';
};

export async function scoreTransaction(req, res, next) {
  try {
    const missing = REQUIRED_FIELDS.filter((field) => req.body[field] === undefined);
    if (missing.length > 0) {
      return res.status(400).json({
        error: `Missing required fields: ${missing.join(', ')}`
      });
    }

    const mlResponse = await requestMlScore(req.body);
    const decision = decisionFromRisk(mlResponse.risk_score);

    return res.json({
      transaction_id: req.body.transaction_id || null,
      risk_score: mlResponse.risk_score,
      confidence_band: mlResponse.confidence_band,
      decision,
      nearest_neighbors: mlResponse.nearest_neighbors,
      fraud_ratio_neighbors: mlResponse.fraud_ratio_neighbors,
      distances: mlResponse.distances,
      rationale: mlResponse.rationale,
      thresholds: {
        low_threshold: LOW_THRESHOLD,
        high_threshold: HIGH_THRESHOLD
      }
    });
  } catch (err) {
    return next(err);
  }
}
