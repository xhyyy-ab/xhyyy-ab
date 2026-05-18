const { request } = require('../utils/request');

async function login(code, userInfo) {
    const response = await request({
        url: `${getApp().globalData.baseUrl}/auth/login`,
        method: 'POST',
        data: {
            code,
            userInfo: userInfo ? {
                nickName: userInfo.nickName,
                avatarUrl: userInfo.avatarUrl
            } : null
        }
    });

    if (response.code === 0) {
        const { token, refreshToken, expiresIn, user } = response.data;
        wx.setStorageSync('access_token', token);
        wx.setStorageSync('refresh_token', refreshToken);
        wx.setStorageSync('token_expires', Date.now() + expiresIn * 1000);
        wx.setStorageSync('user_info', user);
        
        const app = getApp();
        app.globalData.isLoggedIn = true;
        app.globalData.userInfo = user;
        
        return response.data;
    } else {
        throw new Error(response.message);
    }
}

function checkLogin() {
    return getApp().globalData.isLoggedIn;
}

function logout() {
    getApp().clearLoginState();
}

function getUserInfo() {
    return wx.getStorageSync('user_info');
}

module.exports = {
    login,
    checkLogin,
    logout,
    getUserInfo
};
