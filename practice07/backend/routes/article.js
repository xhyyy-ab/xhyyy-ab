const express = require('express');
const router = express.Router();
const articleController = require('../controllers/articleController');

router.get('/', articleController.getArticles);

router.get('/search', articleController.searchArticles);

router.get('/:id', articleController.getArticleById);

router.get('/:articleId/related', articleController.getRelatedArticles);

module.exports = router;
