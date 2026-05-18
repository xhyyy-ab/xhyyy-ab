class BusinessError extends Error {
    constructor(code, message) {
        super(message);
        this.code = code;
        this.name = 'BusinessError';
    }
}

class ErrorWithCode extends Error {
    constructor(message, code) {
        super(message);
        this.code = code;
        this.name = 'ErrorWithCode';
    }
}

const errorHandler = (err, req, res, next) => {
    const requestId = req.headers['x-request-id'] || require('uuid').v4();
    
    if (err instanceof BusinessError) {
        return res.status(400).json({
            code: err.code,
            message: err.message,
            requestId
        });
    }

    if (err.name === 'UnauthorizedError' || err.name === 'JsonWebTokenError') {
        return res.status(401).json({
            code: 4101,
            message: '请先登录',
            requestId
        });
    }

    if (err.name === 'TokenExpiredError') {
        return res.status(401).json({
            code: 4102,
            message: '登录已过期，请重新登录',
            requestId
        });
    }

    console.error('未处理的错误:', err);
    
    return res.status(500).json({
        code: 5000,
        message: process.env.NODE_ENV === 'production' ? '服务器内部错误' : err.message,
        requestId
    });
};

module.exports = {
    BusinessError,
    ErrorWithCode,
    errorHandler
};
