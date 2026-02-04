const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8001';

export async function requestMlScore(payload) {
  const response = await fetch(`${ML_SERVICE_URL}/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const details = await response.text();
    const error = new Error(`ML service error (${response.status}): ${details}`);
    error.status = 502;
    throw error;
  }

  return response.json();
}
