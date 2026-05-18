const express = require('express');
const router = express.Router();
const rateLimit = require('express-rate-limit');
const authController = require('../controllers/authController');

const loginLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 10,
    message: {
        code: 4299,
        message: '请求过于频繁，请稍后再试'
    }
});

router.post('/login', loginLimiter, authController.wxLogin);

router.post('/refresh', authController.refreshToken);

module.exports = router;
