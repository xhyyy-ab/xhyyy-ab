const express = require('express');
const router = express.Router();
const { upload, uploadImage } = require('../controllers/uploadController');
const authMiddleware = require('../middleware/auth');

router.post('/image', authMiddleware, upload.single('image'), uploadImage);

module.exports = router;
