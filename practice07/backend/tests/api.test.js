const request = require('supertest');
const app = require('../server');
const mongoose = require('mongoose');
const User = require('../models/User');
const Article = require('../models/Article');
const DiagnosisRecord = require('../models/DiagnosisRecord');

describe('认证模块测试', () => {
    beforeAll(async () => {
        await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/skincheck_test');
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    beforeEach(async () => {
        await User.deleteMany({});
    });

    describe('POST /api/v1/auth/login', () => {
        test('TC-API-AUTH-003: 缺少必填参数', async () => {
            const response = await request(app)
                .post('/api/v1/auth/login')
                .send({ userInfo: {} });

            expect(response.status).toBe(400);
            expect(response.body.code).toBe(4001);
            expect(response.body.message).toContain('登录凭证无效');
        });

        test('TC-API-AUTH-002: 无效code', async () => {
            const response = await request(app)
                .post('/api/v1/auth/login')
                .send({ code: 'invalid' });

            expect(response.status).toBe(400);
            expect(response.body.code).toBe(4002);
        });
    });
});

describe('AI识别模块测试', () => {
    let token;
    let userId;

    beforeAll(async () => {
        await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/skincheck_test');
        
        const user = await User.create({
            unionId: 'test_union_id',
            openId: 'test_open_id',
            nickName: '测试用户',
            avatarUrl: 'https://example.com/avatar.jpg'
        });
        userId = user.unionId;
        
        const jwt = require('jsonwebtoken');
        token = jwt.sign(
            { unionId: user.unionId, type: 'access' },
            process.env.JWT_SECRET || 'test-secret',
            { expiresIn: '2h' }
        );
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    beforeEach(async () => {
        await DiagnosisRecord.deleteMany({});
    });

    describe('POST /api/v1/diagnosis/analyze', () => {
        test('TC-API-DIAG-002: 未授权访问', async () => {
            const response = await request(app)
                .post('/api/v1/diagnosis/analyze')
                .send({ imageUrls: ['https://example.com/image.jpg'] });

            expect(response.status).toBe(401);
            expect(response.body.code).toBe(4101);
        });

        test('TC-API-DIAG-003: 图片数量超限', async () => {
            const response = await request(app)
                .post('/api/v1/diagnosis/analyze')
                .set('Authorization', `Bearer ${token}`)
                .send({
                    imageUrls: ['url1', 'url2', 'url3', 'url4']
                });

            expect(response.status).toBe(400);
            expect(response.body.code).toBe(3102);
            expect(response.body.message).toContain('最多上传3张照片');
        });

        test('TC-API-DIAG-001: 正常识别请求', async () => {
            const response = await request(app)
                .post('/api/v1/diagnosis/analyze')
                .set('Authorization', `Bearer ${token}`)
                .send({
                    imageUrls: ['https://example.com/test.jpg'],
                    bodyPart: 'limb'
                });

            expect(response.status).toBe(200);
            expect(response.body.code).toBe(0);
            expect(response.body.data).toHaveProperty('recordId');
            expect(response.body.data).toHaveProperty('status');
        });
    });
});

describe('科普内容模块测试', () => {
    beforeAll(async () => {
        await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/skincheck_test');
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    beforeEach(async () => {
        await Article.deleteMany({});
        
        await Article.create([
            {
                id: 'article-001',
                title: '湿疹的日常护理',
                summary: '湿疹是一种常见的皮肤病...',
                coverImage: 'https://example.com/cover1.jpg',
                content: '<p>详细内容...</p>',
                category: 'by_type',
                tags: ['湿疹', '护理'],
                reviewStatus: 'published',
                views: 1200
            },
            {
                id: 'article-002',
                title: '如何预防手足癣',
                summary: '手足癣是由真菌感染引起的...',
                coverImage: 'https://example.com/cover2.jpg',
                content: '<p>详细内容...</p>',
                category: 'by_type',
                tags: ['真菌', '预防'],
                reviewStatus: 'published',
                views: 892
            }
        ]);
    });

    describe('GET /api/v1/articles', () => {
        test('应该返回文章列表', async () => {
            const response = await request(app)
                .get('/api/v1/articles')
                .query({ page: 1, pageSize: 10 });

            expect(response.status).toBe(200);
            expect(response.body.code).toBe(0);
            expect(response.body.data.list).toHaveLength(2);
            expect(response.body.data.pagination).toHaveProperty('total', 2);
        });

        test('按分类筛选文章', async () => {
            const response = await request(app)
                .get('/api/v1/articles')
                .query({ category: 'by_type', page: 1, pageSize: 10 });

            expect(response.status).toBe(200);
            expect(response.body.data.list).toHaveLength(2);
        });
    });

    describe('GET /api/v1/articles/:id', () => {
        test('应该返回文章详情', async () => {
            const response = await request(app)
                .get('/api/v1/articles/article-001');

            expect(response.status).toBe(200);
            expect(response.body.code).toBe(0);
            expect(response.body.data.title).toBe('湿疹的日常护理');
        });

        test('文章不存在', async () => {
            const response = await request(app)
                .get('/api/v1/articles/not-exist');

            expect(response.status).toBe(400);
            expect(response.body.code).toBe(3301);
        });
    });
});

describe('用户中心模块测试', () => {
    let token;
    let userId;

    beforeAll(async () => {
        await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/skincheck_test');
        
        const user = await User.create({
            unionId: 'test_user_favorites',
            openId: 'test_open_favorites',
            nickName: '测试用户',
            avatarUrl: 'https://example.com/avatar.jpg'
        });
        userId = user.unionId;
        
        const jwt = require('jsonwebtoken');
        token = jwt.sign(
            { unionId: user.unionId, type: 'access' },
            process.env.JWT_SECRET || 'test-secret',
            { expiresIn: '2h' }
        );
    });

    afterAll(async () => {
        await mongoose.connection.close();
    });

    describe('GET /api/v1/user/info', () => {
        test('应该返回用户信息', async () => {
            const response = await request(app)
                .get('/api/v1/user/info')
                .set('Authorization', `Bearer ${token}`);

            expect(response.status).toBe(200);
            expect(response.body.code).toBe(0);
            expect(response.body.data.nickName).toBe('测试用户');
        });
    });
});
