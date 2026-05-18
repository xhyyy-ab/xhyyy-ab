const Article = require('../models/Article');
const { BusinessError } = require('../middleware/errorHandler');
const { v4: uuidv4 } = require('uuid');

async function getArticles(req, res, next) {
    try {
        const { category, tag, page = 1, pageSize = 10 } = req.query;
        
        const query = { reviewStatus: 'published' };
        
        if (category) {
            query.category = category;
        }
        
        if (tag) {
            query.tags = tag;
        }

        const total = await Article.countDocuments(query);
        const articles = await Article.find(query)
            .sort({ views: -1, createdAt: -1 })
            .skip((parseInt(page) - 1) * parseInt(pageSize))
            .limit(parseInt(pageSize));

        res.json({
            code: 0,
            message: 'success',
            data: {
                list: articles,
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

async function getArticleById(req, res, next) {
    try {
        const { id } = req.params;
        
        const article = await Article.findOne({ id, reviewStatus: 'published' });
        
        if (!article) {
            throw new BusinessError(3301, '文章不存在');
        }

        article.views += 1;
        await article.save();

        res.json({
            code: 0,
            message: 'success',
            data: article,
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function searchArticles(req, res, next) {
    try {
        const { keyword, page = 1, pageSize = 10 } = req.query;
        
        if (!keyword) {
            throw new BusinessError(3302, '搜索关键词不能为空');
        }

        const query = {
            reviewStatus: 'published',
            $or: [
                { title: { $regex: keyword, $options: 'i' } },
                { summary: { $regex: keyword, $options: 'i' } },
                { tags: { $in: [new RegExp(keyword, 'i')] } }
            ]
        };

        const total = await Article.countDocuments(query);
        const articles = await Article.find(query)
            .sort({ views: -1, createdAt: -1 })
            .skip((parseInt(page) - 1) * parseInt(pageSize))
            .limit(parseInt(pageSize));

        res.json({
            code: 0,
            message: 'success',
            data: {
                list: articles,
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

async function getRelatedArticles(req, res, next) {
    try {
        const { articleId } = req.params;
        
        const article = await Article.findOne({ id: articleId });
        
        if (!article) {
            throw new BusinessError(3301, '文章不存在');
        }

        const relatedArticles = await Article.find({
            tags: { $in: article.tags },
            reviewStatus: 'published',
            id: { $ne: articleId }
        })
        .sort({ views: -1, createdAt: -1 })
        .limit(3);

        res.json({
            code: 0,
            message: 'success',
            data: relatedArticles,
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

module.exports = {
    getArticles,
    getArticleById,
    searchArticles,
    getRelatedArticles
};
