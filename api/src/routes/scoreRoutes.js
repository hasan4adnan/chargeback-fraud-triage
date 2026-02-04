import { Router } from 'express';
import { scoreTransaction } from '../controllers/scoreController.js';

const router = Router();

router.post('/score_transaction', scoreTransaction);

export default router;
