import express from 'express';
import scoreRoutes from './routes/scoreRoutes.js';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/health', (_, res) => {
  res.json({ status: 'ok', service: 'fraud-triage-api' });
});

app.use('/', scoreRoutes);

app.use((err, _, res, __) => {
  const status = err.status || 500;
  res.status(status).json({ error: err.message || 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`API listening on port ${PORT}`);
});
