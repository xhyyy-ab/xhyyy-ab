const User = require('../models/User');
const DiagnosisRecord = require('../models/DiagnosisRecord');
const Favorite = require('../models/Favorite');
const Article = require('../models/Article');
const { BusinessError } = require('../middleware/errorHandler');
const { v4: uuidv4 } = require('uuid');

async function getUserInfo(req, res, next) {
    try {
        const unionId = req.user.unionId;
        
        const user = await User.findOne({ unionId });
        
        if (!user) {
            throw new BusinessError(4005, '用户不存在');
        }

        const diagnosisCount = await DiagnosisRecord.countDocuments({ 
            userId: unionId, 
            status: 'completed' 
        });

        res.json({
            code: 0,
            message: 'success',
            data: {
                unionId: user.unionId,
                nickName: user.nickName,
                avatarUrl: user.avatarUrl,
                diagnosisCount,
                createdAt: user.createdAt
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function getHistory(req, res, next) {
    try {
        const unionId = req.user.unionId;
        const { page = 1, pageSize = 20 } = req.query;
        
        const total = await DiagnosisRecord.countDocuments({ 
            userId: unionId,
            status: { $in: ['completed', 'failed'] }
        });
        
        const records = await DiagnosisRecord.find({ 
            userId: unionId,
            status: { $in: ['completed', 'failed'] }
        })
        .sort({ createdAt: -1 })
        .skip((parseInt(page) - 1) * parseInt(pageSize))
        .limit(parseInt(pageSize));

        res.json({
            code: 0,
            message: 'success',
            data: {
                list: records,
                pagination: {
                    page: parseInt(page),
                    pageSize: parseInt(pageSize),
                    total,
                    hasMore: (parseInt(page) * parseInt(pageSize)) < total
                }
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function deleteHistoryRecord(req, res, next) {
    try {
        const { recordId } = req.params;
        const unionId = req.user.unionId;
        
        const record = await DiagnosisRecord.findOne({ id: recordId });
        
        if (!record) {
            throw new BusinessError(3201, '记录不存在');
        }

        if (record.userId !== unionId) {
            throw new BusinessError(3202, '无权删除该记录');
        }

        await DiagnosisRecord.deleteOne({ id: recordId });

        res.json({
            code: 0,
            message: '删除成功',
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function addFavorite(req, res, next) {
    try {
        const { articleId } = req.body;
        const unionId = req.user.unionId;
        
        if (!articleId) {
            throw new BusinessError(3501, '文章ID不能为空');
        }

        const article = await Article.findOne({ id: articleId, reviewStatus: 'published' });
        if (!article) {
            throw new BusinessError(3301, '文章不存在');
        }

        const existingFavorite = await Favorite.findOne({ userId: unionId, articleId });
        if (existingFavorite) {
            throw new BusinessError(3502, '已收藏该文章');
        }

        await Favorite.create({
            id: uuidv4(),
            userId: unionId,
            articleId,
            createdAt: new Date()
        });

        res.json({
            code: 0,
            message: '收藏成功',
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function removeFavorite(req, res, next) {
    try {
        const { articleId } = req.params;
        const unionId = req.user.unionId;
        
        const favorite = await Favorite.findOne({ userId: unionId, articleId });
        if (!favorite) {
            throw new BusinessError(3503, '未收藏该文章');
        }

        await Favorite.deleteOne({ userId: unionId, articleId });

        res.json({
            code: 0,
            message: '取消收藏成功',
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function getFavorites(req, res, next) {
    try {
        const unionId = req.user.unionId;
        const { page = 1, pageSize = 20 } = req.query;
        
        const favorites = await Favorite.find({ userId: unionId })
            .sort({ createdAt: -1 })
            .skip((parseInt(page) - 1) * parseInt(pageSize))
            .limit(parseInt(pageSize));

        const articleIds = favorites.map(f => f.articleId);
        const articles = await Article.find({ id: { $in: articleIds } });

        const articleMap = {};
        articles.forEach(article => {
            articleMap[article.id] = article;
        });

        const result = favorites.map(favorite => ({
            ...articleMap[favorite.articleId]?.toObject(),
            favoriteId: favorite.id,
            favoriteAt: favorite.createdAt
        })).filter(item => item.id);

        const total = await Favorite.countDocuments({ userId: unionId });

        res.json({
            code: 0,
            message: 'success',
            data: {
                list: result,
                pagination: {
                    page: parseInt(page),
                    pageSize: parseInt(pageSize),
                    total,
                    hasMore: (parseInt(page) * parseInt(pageSize)) < total
                }
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

module.exports = {
    getUserInfo,
    getHistory,
    deleteHistoryRecord,
    addFavorite,
    removeFavorite,
    getFavorites
};
