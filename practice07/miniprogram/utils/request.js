const BASE_URL = getApp().globalData.baseUrl;

function getToken() {
    return wx.getStorageSync('access_token');
}

function getRefreshToken() {
    return wx.getStorageSync('refresh_token');
}

async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        throw new Error('无刷新令牌，需要重新登录');
    }

    const response = await request({
        url: `${BASE_URL}/auth/refresh`,
        method: 'POST',
        data: { refreshToken },
        skipAuthRefresh: true
    });

    if (response.code === 0) {
        const { token, expiresIn } = response.data;
        wx.setStorageSync('access_token', token);
        wx.setStorageSync('token_expires', Date.now() + expiresIn * 1000);
        return token;
    } else {
        getApp().clearLoginState();
        throw new Error('登录已过期，请重新登录');
    }
}

function request(options) {
    return new Promise((resolve, reject) => {
        const token = getToken();
        
        const header = {
            'Content-Type': 'application/json',
            ...options.header
        };

        if (token) {
            header['Authorization'] = `Bearer ${token}`;
        }

        wx.request({
            url: options.url,
            method: options.method || 'GET',
            data: options.data,
            header: header,
            timeout: options.timeout || 10000,
            success: async (res) => {
                if (res.statusCode === 401 && !options.skipAuthRefresh) {
                    try {
                        await refreshAccessToken();
                        const retryResponse = await request({
                            ...options,
                            skipAuthRefresh: true
                        });
                        resolve(retryResponse);
                    } catch (err) {
                        reject(err);
                    }
                } else if (res.statusCode === 200) {
                    resolve(res.data);
                } else {
                    reject(new Error(res.data.message || '请求失败'));
                }
            },
            fail: (err) => {
                reject(new Error(err.errMsg || '网络请求失败'));
            }
        });
    });
}

function uploadFile(filePath, formData = {}) {
    return new Promise((resolve, reject) => {
        const token = getToken();
        
        wx.uploadFile({
            url: `${BASE_URL}/upload/image`,
            filePath: filePath,
            name: 'image',
            formData: formData,
            header: {
                'Authorization': `Bearer ${token}`
            },
            success: (res) => {
                const data = JSON.parse(res.data);
                if (data.code === 0) {
                    resolve(data.data);
                } else {
                    reject(new Error(data.message || '上传失败'));
                }
            },
            fail: (err) => {
                reject(new Error(err.errMsg || '上传失败'));
            }
        });
    });
}

module.exports = {
    request,
    uploadFile,
    getToken,
    refreshAccessToken
};
