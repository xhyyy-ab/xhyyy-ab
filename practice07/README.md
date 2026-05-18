# SkinCheck 皮肤病智能自查小程序

一款面向普通用户的皮肤病智能自查与科普工具微信小程序。

## 项目结构

```
practice07/
├── backend/                 # 后端服务
│   ├── controllers/        # 控制器
│   ├── models/             # 数据模型
│   ├── routes/             # 路由
│   ├── middleware/         # 中间件
│   ├── utils/              # 工具函数
│   ├── tests/              # 测试文件
│   ├── server.js           # 服务入口
│   └── package.json        # 依赖配置
├── miniprogram/            # 微信小程序前端
│   ├── pages/              # 页面
│   ├── components/         # 组件
│   ├── utils/              # 工具函数
│   ├── services/           # 服务层
│   ├── app.js              # 小程序入口
│   ├── app.json            # 小程序配置
│   └── app.wxss            # 全局样式
├── requirement.md          # 需求文档
├── spec.md                 # 规格文档
├── api.md                  # API文档
├── test.md                 # 测试文档
└── TEST_REPORT.md          # 测试报告
```

## 功能特性

### 核心功能
- ✅ 微信一键登录
- ✅ AI皮肤病识别（支持1-3张照片）
- ✅ 识别结果展示（置信度分级）
- ✅ 医疗免责声明强制交互
- ✅ 科普文章推荐与浏览
- ✅ 文章收藏功能
- ✅ 识别历史记录
- ✅ 个人中心

### 技术特性
- RESTful API设计
- JWT认证机制
- MongoDB数据存储
- 响应式UI设计
- 完整的错误处理
- 安全防护（Helmet、Rate Limit）

## 快速开始

### 环境要求

- Node.js 18+
- MongoDB 6.0+
- Redis 7.0+ (可选)
- 微信开发者工具

### 后端安装与运行

```bash
# 进入后端目录
cd backend

# 安装依赖
npm install

# 复制环境变量配置
cp .env.example .env

# 编辑.env文件，配置必要的参数
# - MONGODB_URI: MongoDB连接字符串
# - JWT_SECRET: JWT密钥
# - WECHAT_APP_ID: 微信小程序AppID
# - WECHAT_APP_SECRET: 微信小程序AppSecret

# 启动开发服务器
npm run dev

# 或启动生产服务器
npm start
```

### 运行测试

```bash
# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm test -- --coverage

# 监听模式运行测试
npm run test:watch
```

### 小程序配置

1. 打开微信开发者工具
2. 导入 `miniprogram` 目录
3. 在 `app.js` 中修改 `baseUrl` 为后端服务地址
4. 点击"编译"运行小程序

## API文档

### 认证接口

#### POST /api/v1/auth/login
微信登录

**请求参数:**
```json
{
  "code": "微信登录凭证",
  "userInfo": {
    "nickName": "用户昵称",
    "avatarUrl": "用户头像URL"
  }
}
```

**响应:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "JWT令牌",
    "refreshToken": "刷新令牌",
    "expiresIn": 7200,
    "user": {
      "unionId": "用户唯一标识",
      "nickName": "昵称",
      "avatarUrl": "头像",
      "isNew": false
    }
  }
}
```

### AI识别接口

#### POST /api/v1/diagnosis/analyze
AI识别分析

**请求参数:**
```json
{
  "imageUrls": ["图片URL1", "图片URL2"],
  "bodyPart": "limb"
}
```

**响应:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "recordId": "记录ID",
    "status": "completed",
    "result": {
      "primary": {
        "diseaseId": "疾病ID",
        "diseaseName": "疾病名称",
        "confidence": 0.87,
        "description": "简要说明",
        "suggestedDepartment": "建议科室"
      },
      "alternatives": [],
      "urgencyLevel": "medium",
      "disclaimer": "免责声明文本"
    },
    "relatedArticles": []
  }
}
```

### 科普内容接口

#### GET /api/v1/articles
获取文章列表

**查询参数:**
- `category`: 分类 (by_location, by_type, seasonal)
- `tag`: 标签
- `page`: 页码
- `pageSize`: 每页数量

#### GET /api/v1/articles/:id
获取文章详情

### 用户中心接口

#### GET /api/v1/user/info
获取用户信息

#### GET /api/v1/user/history
获取识别历史

#### POST /api/v1/user/favorites
添加收藏

## 测试

项目包含完整的测试套件：

- **单元测试**: 后端业务逻辑测试
- **接口测试**: API集成测试
- **功能测试**: 前端功能测试

详细测试报告请查看 [TEST_REPORT.md](./TEST_REPORT.md)

## 部署

### 生产环境配置

1. 配置MongoDB生产数据库
2. 配置Redis缓存服务
3. 配置腾讯云COS对象存储
4. 配置真实的微信小程序AppID和AppSecret
5. 接入真实的AI识别服务
6. 配置HTTPS证书
7. 配置进程管理器（PM2）

### 安全建议

- 使用环境变量管理敏感信息
- 启用HTTPS
- 配置CORS白名单
- 启用Rate Limiting
- 定期更新依赖包

## 开发团队

- 产品设计: 产品团队
- 后端开发: 后端团队
- 前端开发: 前端团队
- 测试: 测试团队

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-05-17)
- 初始版本发布
- 实现核心功能
- 完成测试验证
