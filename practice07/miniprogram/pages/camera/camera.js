const { uploadImages, analyzeDiagnosis } = require('../../services/diagnosis');

Page({
    data: {
        images: [],
        selectedBodyPart: 'other',
        showGuide: true,
        bodyParts: [
            { label: '面部', value: 'face' },
            { label: '躯干', value: 'trunk' },
            { label: '四肢', value: 'limb' },
            { label: '手足', value: 'hand_foot' },
            { label: '其他', value: 'other' }
        ]
    },

    onLoad() {
        const hasShownGuide = wx.getStorageSync('has_shown_camera_guide');
        if (hasShownGuide) {
            this.setData({ showGuide: false });
        }
    },

    onCloseGuide() {
        this.setData({ showGuide: false });
        wx.setStorageSync('has_shown_camera_guide', true);
    },

    onChooseImage() {
        const remaining = 3 - this.data.images.length;
        
        wx.showActionSheet({
            itemList: ['拍照', '从相册选择'],
            success: (res) => {
                const sourceType = res.tapIndex === 0 ? ['camera'] : ['album'];
                
                wx.chooseMedia({
                    count: remaining,
                    mediaType: ['image'],
                    sourceType: sourceType,
                    sizeType: ['compressed'],
                    success: (res) => {
                        const newImages = res.tempFiles.map(file => file.tempFilePath);
                        this.setData({
                            images: [...this.data.images, ...newImages]
                        });
                    }
                });
            }
        });
    },

    onDeleteImage(e) {
        const { index } = e.currentTarget.dataset;
        const images = [...this.data.images];
        images.splice(index, 1);
        this.setData({ images });
    },

    onSelectBodyPart(e) {
        const { value } = e.currentTarget.dataset;
        this.setData({ selectedBodyPart: value });
    },

    async onAnalyze() {
        if (this.data.images.length === 0) {
            wx.showToast({
                title: '请至少上传1张照片',
                icon: 'none'
            });
            return;
        }

        try {
            wx.showLoading({ title: '上传中...', mask: true });

            const uploadResults = await uploadImages(this.data.images);
            const imageUrls = uploadResults.map(result => result.url);

            wx.hideLoading();
            wx.navigateTo({ url: '/pages/analyzing/analyzing' });

            const result = await analyzeDiagnosis(imageUrls, this.data.selectedBodyPart);

            const app = getApp();
            app.globalData.diagnosisResult = result;

            wx.redirectTo({
                url: `/pages/result/result?recordId=${result.recordId}`
            });
        } catch (error) {
            wx.hideLoading();
            console.error('分析失败:', error);
            wx.showToast({
                title: error.message || '分析失败',
                icon: 'none'
            });
        }
    }
});
