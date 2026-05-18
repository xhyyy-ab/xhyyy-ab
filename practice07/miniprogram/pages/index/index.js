const { request } = require('../../utils/request');
const { checkLogin } = require('../../utils/auth');

Page({
    data: {
        banners: [],
        articles: [],
        loading: true,
        page: 1,
        hasMore: true
    },

    onLoad() {
        this.loadBanners();
        this.loadArticles();
    },

    onPullDownRefresh() {
        this.setData({ page: 1, hasMore: true });
        this.loadArticles().then(() => {
            wx.stopPullDownRefresh();
        });
    },

    onReachBottom() {
        if (this.data.hasMore && !this.data.loading) {
            this.loadMoreArticles();
        }
    },

    async loadBanners() {
        this.setData({
            banners: [
                { id: 1, image: '/assets/images/banner1.jpg', link: '' },
                { id: 2, image: '/assets/images/banner2.jpg', link: '' },
                { id: 3, image: '/assets/images/banner3.jpg', link: '' }
            ]
        });
    },

    async loadArticles() {
        try {
            this.setData({ loading: true });
            
            const response = await request({
                url: `${getApp().globalData.baseUrl}/articles`,
                data: { page: 1, pageSize: 10 }
            });

            if (response.code === 0) {
                this.setData({
                    articles: response.data.list,
                    hasMore: response.data.pagination.hasMore,
                    loading: false
                });
            }
        } catch (error) {
            console.error('加载文章失败:', error);
            wx.showToast({
                title: '加载失败',
                icon: 'none'
            });
            this.setData({ loading: false });
        }
    },

    async loadMoreArticles() {
        try {
            const nextPage = this.data.page + 1;
            
            const response = await request({
                url: `${getApp().globalData.baseUrl}/articles`,
                data: { page: nextPage, pageSize: 10 }
            });

            if (response.code === 0) {
                this.setData({
                    articles: [...this.data.articles, ...response.data.list],
                    page: nextPage,
                    hasMore: response.data.pagination.hasMore
                });
            }
        } catch (error) {
            console.error('加载更多失败:', error);
        }
    },

    onStartCheck() {
        if (!checkLogin()) {
            wx.navigateTo({
                url: '/pages/login/login'
            });
        } else {
            wx.navigateTo({
                url: '/pages/camera/camera'
            });
        }
    },

    onArticleTap(e) {
        const { id } = e.currentTarget.dataset;
        wx.navigateTo({
            url: `/pages/article-detail/article-detail?id=${id}`
        });
    },

    onMoreArticles() {
        wx.switchTab({
            url: '/pages/articles/articles'
        });
    },

    onBannerTap(e) {
        const { url } = e.currentTarget.dataset;
        if (url) {
            wx.navigateTo({ url });
        }
    }
});
