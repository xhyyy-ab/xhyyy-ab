const { login } = require('../../utils/auth');

Page({
    data: {},

    async onLogin() {
        try {
            wx.showLoading({ title: '登录中...' });

            const { code } = await wx.login({ timeout: 10000 });
            if (!code) {
                throw new Error('获取登录凭证失败');
            }

            let userInfo = null;
            try {
                const { userInfo: info } = await wx.getUserProfile({
                    desc: '用于完善用户资料'
                });
                userInfo = info;
            } catch (e) {
                console.log('用户拒绝授权头像昵称');
            }

            await login(code, userInfo);

            wx.hideLoading();
            
            wx.showToast({
                title: '登录成功',
                icon: 'success'
            });

            setTimeout(() => {
                wx.navigateBack();
            }, 1500);
        } catch (error) {
            wx.hideLoading();
            console.error('登录失败:', error);
            wx.showToast({
                title: error.message || '登录失败',
                icon: 'none'
            });
        }
    },

    onPrivacyPolicy() {
        wx.navigateTo({
            url: '/pages/settings/settings?type=privacy'
        });
    },

    onUserAgreement() {
        wx.navigateTo({
            url: '/pages/settings/settings?type=agreement'
        });
    }
});
