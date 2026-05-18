const express = require('express');
const router = express.Router();
const diagnosisController = require('../controllers/diagnosisController');
const authMiddleware = require('../middleware/auth');

router.post('/analyze', authMiddleware, diagnosisController.analyzeDiagnosis);

router.get('/record/:recordId', authMiddleware, diagnosisController.getDiagnosisRecord);

module.exports = router;
