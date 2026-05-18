require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');

const authRoutes = require('./routes/auth');
const diagnosisRoutes = require('./routes/diagnosis');
const articleRoutes = require('./routes/article');
const userRoutes = require('./routes/user');
const uploadRoutes = require('./routes/upload');

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use((req, res, next) => {
    logger.info(`${req.method} ${req.path}`, {
        ip: req.ip,
        userAgent: req.get('user-agent')
    });
    next();
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/diagnosis', diagnosisRoutes);
app.use('/api/v1/articles', articleRoutes);
app.use('/api/v1/user', userRoutes);
app.use('/api/v1/upload', uploadRoutes);

app.use((req, res) => {
    res.status(404).json({
        code: 404,
        message: '接口不存在'
    });
});

app.use(errorHandler);

const PORT = process.env.PORT || 3000;

mongoose.connect(process.env.MONGODB_URI)
    .then(() => {
        logger.info('MongoDB 连接成功');
        app.listen(PORT, () => {
            logger.info(`服务器运行在端口 ${PORT}`);
        });
    })
    .catch(err => {
        logger.error('MongoDB 连接失败:', err);
        process.exit(1);
    });

module.exports = app;
