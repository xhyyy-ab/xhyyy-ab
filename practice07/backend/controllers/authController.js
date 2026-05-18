const jwt = require('jsonwebtoken');
const axios = require('axios');
const User = require('../models/User');
const { BusinessError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');

const WX_APP_ID = process.env.WECHAT_APP_ID;
const WX_APP_SECRET = process.env.WECHAT_APP_SECRET;
const JWT_SECRET = process.env.JWT_SECRET;

async function wxLogin(req, res, next) {
    try {
        const { code, userInfo } = req.body;

        if (!code || code.length < 10) {
            throw new BusinessError(4001, '登录凭证无效');
        }

        const wxResponse = await axios.get('https://api.weixin.qq.com/sns/jscode2session', {
            params: {
                appid: WX_APP_ID,
                secret: WX_APP_SECRET,
                js_code: code,
                grant_type: 'authorization_code'
            }
        });

        if (wxResponse.data.errcode) {
            logger.error('微信登录失败', { errcode: wxResponse.data.errcode });
            throw new BusinessError(4002, '微信登录失败，请重试');
        }

        const { openid, unionid, session_key } = wxResponse.data;
        const unionId = unionid || openid;

        let user = await User.findOne({ unionId });
        let isNewUser = false;

        if (!user) {
            user = await User.create({
                unionId,
                openId: openid,
                nickName: userInfo?.nickName || '微信用户',
                avatarUrl: userInfo?.avatarUrl || '',
                createdAt: new Date(),
                lastLoginAt: new Date()
            });
            isNewUser = true;
            logger.info('新用户注册', { unionId });
        } else {
            user.lastLoginAt = new Date();
            if (userInfo?.nickName) user.nickName = userInfo.nickName;
            if (userInfo?.avatarUrl) user.avatarUrl = userInfo.avatarUrl;
            await user.save();
        }

        const tokenPayload = {
            unionId: user.unionId,
            type: 'access',
            iat: Math.floor(Date.now() / 1000)
        };

        const token = jwt.sign(tokenPayload, JWT_SECRET, { expiresIn: '2h' });
        const refreshToken = jwt.sign(
            { unionId: user.unionId, type: 'refresh' },
            JWT_SECRET,
            { expiresIn: '7d' }
        );

        res.json({
            code: 0,
            message: 'success',
            data: {
                token,
                refreshToken,
                expiresIn: 7200,
                user: {
                    unionId: user.unionId,
                    nickName: user.nickName,
                    avatarUrl: user.avatarUrl,
                    isNew: isNewUser
                }
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

async function refreshToken(req, res, next) {
    try {
        const { refreshToken } = req.body;
        
        if (!refreshToken) {
            throw new BusinessError(4003, '刷新令牌不能为空');
        }

        let payload;
        try {
            payload = jwt.verify(refreshToken, JWT_SECRET);
        } catch (err) {
            if (err.name === 'TokenExpiredError') {
                throw new BusinessError(4003, '登录已过期，请重新登录');
            }
            throw new BusinessError(4004, '登录状态无效');
        }

        if (payload.type !== 'refresh') {
            throw new BusinessError(4004, '登录状态无效');
        }

        const user = await User.findOne({ unionId: payload.unionId });
        if (!user) {
            throw new BusinessError(4005, '用户不存在');
        }

        const newToken = jwt.sign(
            { unionId: user.unionId, type: 'access', iat: Math.floor(Date.now() / 1000) },
            JWT_SECRET,
            { expiresIn: '2h' }
        );

        res.json({
            code: 0,
            message: 'success',
            data: {
                token: newToken,
                expiresIn: 7200
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

module.exports = {
    wxLogin,
    refreshToken
};
