const app = getApp();

Page({
    data: {
        recordId: '',
        result: null,
        disclaimerConfirmed: false,
        disclaimerScrolledToBottom: false,
        urgencyText: ''
    },

    onLoad(options) {
        const { recordId } = options;
        
        if (app.globalData.diagnosisResult) {
            const result = app.globalData.diagnosisResult;
            this.setData({
                recordId,
                result,
                urgencyText: this.getUrgencyText(result.result.urgencyLevel)
            });
            app.globalData.diagnosisResult = null;
        } else {
            this.loadResult(recordId);
        }
    },

    async loadResult(recordId) {
        try {
            wx.showLoading({ title: '加载中...' });
            
            const { getDiagnosisRecord } = require('../../services/diagnosis');
            const result = await getDiagnosisRecord(recordId);
            
            this.setData({
                recordId,
                result,
                urgencyText: this.getUrgencyText(result.result.urgencyLevel)
            });
            
            wx.hideLoading();
        } catch (error) {
            wx.hideLoading();
            console.error('加载结果失败:', error);
            wx.showToast({
                title: '加载失败',
                icon: 'none'
            });
        }
    },

    getUrgencyText(level) {
        const map = {
            'low': '可观察',
            'medium': '建议近期就诊',
            'high': '建议尽快就医'
        };
        return map[level] || '未知';
    },

    onDisclaimerScrollBottom() {
        this.setData({ disclaimerScrolledToBottom: true });
    },

    onConfirmDisclaimer() {
        if (!this.data.disclaimerScrolledToBottom) {
            return;
        }
        
        this.setData({ disclaimerConfirmed: true });
    },

    onArticleTap(e) {
        const { id } = e.currentTarget.dataset;
        wx.navigateTo({
            url: `/pages/article-detail/article-detail?id=${id}`
        });
    },

    onBackHome() {
        wx.switchTab({
            url: '/pages/index/index'
        });
    },

    onRecheck() {
        wx.redirectTo({
            url: '/pages/camera/camera'
        });
    }
});
