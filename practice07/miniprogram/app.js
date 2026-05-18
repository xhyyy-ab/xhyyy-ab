App({
    globalData: {
        userInfo: null,
        isLoggedIn: false,
        baseUrl: 'http://localhost:3000/api/v1'
    },

    onLaunch() {
        this.checkLoginStatus();
    },

    checkLoginStatus() {
        const token = wx.getStorageSync('access_token');
        const expires = wx.getStorageSync('token_expires');
        
        if (token && expires && Date.now() < expires) {
            this.globalData.isLoggedIn = true;
            this.globalData.userInfo = wx.getStorageSync('user_info');
        } else {
            this.clearLoginState();
        }
    },

    clearLoginState() {
        wx.removeStorageSync('access_token');
        wx.removeStorageSync('refresh_token');
        wx.removeStorageSync('token_expires');
        wx.removeStorageSync('user_info');
        this.globalData.isLoggedIn = false;
        this.globalData.userInfo = null;
    },

    requireLogin(callback) {
        if (this.globalData.isLoggedIn) {
            callback && callback();
        } else {
            wx.navigateTo({
                url: '/pages/login/login'
            });
        }
    }
});
