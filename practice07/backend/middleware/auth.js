const jwt = require('jsonwebtoken');
const { BusinessError } = require('./errorHandler');

const authMiddleware = (req, res, next) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        throw new BusinessError(4101, '请先登录');
    }
    
    const token = authHeader.substring(7);
    
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = {
            unionId: decoded.unionId,
            type: decoded.type
        };
        next();
    } catch (err) {
        if (err.name === 'TokenExpiredError') {
            throw new BusinessError(4102, '登录已过期，请重新登录');
        }
        throw new BusinessError(4101, '登录状态无效');
    }
};

module.exports = authMiddleware;
