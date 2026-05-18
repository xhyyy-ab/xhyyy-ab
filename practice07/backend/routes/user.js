const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const authMiddleware = require('../middleware/auth');

router.get('/info', authMiddleware, userController.getUserInfo);

router.get('/history', authMiddleware, userController.getHistory);

router.delete('/history/:recordId', authMiddleware, userController.deleteHistoryRecord);

router.post('/favorites', authMiddleware, userController.addFavorite);

router.delete('/favorites/:articleId', authMiddleware, userController.removeFavorite);

router.get('/favorites', authMiddleware, userController.getFavorites);

module.exports = router;
