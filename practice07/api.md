# SkinCheck 皮肤病小程序 - API 开发接口文档

> **文档编号**: API-SKC-2026-001
> **版本**: v1.0.0
> **日期**: 2026-05-17
> **依赖**: SPEC-SKC-2026-001, SRS-SKC-2026-001

---

## 目录

1. [概述](#1-概述)
2. [通用规范](#2-通用规范)
3. [认证模块 API](#3-认证模块-api)
4. [AI 识别模块 API](#4-ai-识别模块-api)
5. [科普内容模块 API](#5-科普内容模块-api)
6. [用户中心模块 API](#6-用户中心模块-api)
7. [后端服务伪代码](#7-后端服务伪代码)
8. [前端服务层伪代码](#8-前端服务层伪代码)
9. [数据模型定义](#9-数据模型定义)
10. [错误码表](#10-错误码表)

---

## 1. 概述

### 1.1 文档目的
本文档定义 SkinCheck 小程序前后端交互的所有接口规范，包含请求/响应格式、参数说明、业务逻辑伪代码，供前后端开发人员参考实现。

### 1.2 接口总览

| 模块 | 接口数量 | 核心接口 |
|------|---------|---------|
| 认证模块 | 2 | 微信登录、Token刷新 |
| AI 识别模块 | 3 | 照片上传、AI分析、获取结果 |
| 科普内容模块 | 4 | 文章列表、文章详情、搜索、关联推荐 |
| 用户中心模块 | 4 | 用户信息、历史记录、收藏、设置 |

---

## 2. 通用规范

### 2.1 通信协议
- 协议: HTTPS
- 数据格式: JSON
- 字符编码: UTF-8
- TLS版本: 1.3+

### 2.2 请求规范

```
Headers:
  Content-Type: application/json
  Authorization: Bearer <jwt_token>  (除登录接口外必填)
  X-Request-ID: <uuid>              (请求追踪ID)
  X-Client-Version: 1.0.0          (小程序版本)
```

### 2.3 响应规范

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "requestId": "uuid"
}
```

### 2.4 分页规范

```json
{
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 100,
      "hasMore": true
    }
  }
}
```

---

## 3. 认证模块 API

### 3.1 微信登录

**接口信息**

| 属性 | 值 |
|------|-----|
| 接口名称 | 微信登录 |
| 接口路径 | POST /api/v1/auth/login |
| 是否需要认证 | 否 |
| 调用频率限制 | 10次/分钟/IP |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | string | 是 | wx.login获取的临时登录凭证 |
| userInfo | object | 否 | 微信用户信息 |
| userInfo.nickName | string | 否 | 用户昵称 |
| userInfo.avatarUrl | string | 否 | 用户头像URL |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| token | string | JWT访问令牌 |
| refreshToken | string | JWT刷新令牌 |
| expiresIn | number | token有效期(秒) |
| user | object | 用户信息 |
| user.unionId | string | 用户唯一标识 |
| user.nickName | string | 用户昵称 |
| user.avatarUrl | string | 用户头像 |
| user.isNew | boolean | 是否新用户 |

**后端伪代码**

```javascript
/**
 * 微信登录
 * @param {string} code - 微信临时登录凭证
 * @param {object} userInfo - 用户信息(可选)
 * @returns {object} 登录结果
 */
function wxLogin(code, userInfo) {
    // 1. 参数校验
    if (!code || code.length < 10) {
        throw new BusinessError(4001, "登录凭证无效");
    }

    // 2. 调用微信接口换取OpenID和UnionID
    const wxResponse = callWechatAPI("jscode2session", {
        appid: WX_APP_ID,
        secret: WX_APP_SECRET,
        js_code: code,
        grant_type: "authorization_code"
    });

    if (wxResponse.errcode) {
        logger.error("微信登录失败", { errcode: wxResponse.errcode });
        throw new BusinessError(4002, "微信登录失败，请重试");
    }

    const { openid, unionid, session_key } = wxResponse;

    // 3. 查询或创建用户
    let user = await UserModel.findOne({ unionId: unionid });
    let isNewUser = false;

    if (!user) {
        user = await UserModel.create({
            unionId: unionid,
            openId: openid,
            nickName: userInfo?.nickName || "微信用户",
            avatarUrl: userInfo?.avatarUrl || DEFAULT_AVATAR,
            createdAt: now(),
            lastLoginAt: now()
        });
        isNewUser = true;
        logger.info("新用户注册", { unionId: unionid });
    } else {
        user.lastLoginAt = now();
        if (userInfo?.nickName) user.nickName = userInfo.nickName;
        if (userInfo?.avatarUrl) user.avatarUrl = userInfo.avatarUrl;
        await user.save();
    }

    // 4. 生成JWT Token
    const tokenPayload = {
        unionId: user.unionId,
        type: "access",
        iat: now()
    };

    const token = jwt.sign(tokenPayload, JWT_SECRET, { expiresIn: "2h" });
    const refreshToken = jwt.sign(
        { unionId: user.unionId, type: "refresh" },
        JWT_SECRET,
        { expiresIn: "7d" }
    );

    // 5. 缓存Token到Redis
    await redis.setex(`token:${user.unionId}`, 7200, token);

    // 6. 返回结果
    return {
        token,
        refreshToken,
        expiresIn: 7200,
        user: {
            unionId: user.unionId,
            nickName: user.nickName,
            avatarUrl: user.avatarUrl,
            isNew: isNewUser
        }
    };
}
```

**前端伪代码**

```javascript
/**
 * 微信登录
 * @returns {Promise<object>} 登录结果
 */
async function login() {
    try {
        // 1. 获取微信登录code
        const { code } = await wx.login({ timeout: 10000 });
        if (!code) throw new Error("获取登录凭证失败");

        // 2. 获取用户信息(需用户授权)
        let userInfo = null;
        try {
            const { userInfo: info } = await wx.getUserProfile({
                desc: "用于完善用户资料"
            });
            userInfo = info;
        } catch (e) {
            console.log("用户拒绝授权头像昵称");
        }

        // 3. 调用后端登录接口
        const response = await request.post("/api/v1/auth/login", {
            code,
            userInfo: userInfo ? {
                nickName: userInfo.nickName,
                avatarUrl: userInfo.avatarUrl
            } : null
        });

        // 4. 保存登录态
        if (response.code === 0) {
            const { token, refreshToken, expiresIn, user } = response.data;
            wx.setStorageSync("access_token", token);
            wx.setStorageSync("refresh_token", refreshToken);
            wx.setStorageSync("token_expires", Date.now() + expiresIn * 1000);
            wx.setStorageSync("user_info", user);

            // 5. 新用户引导
            if (user.isNew) showPrivacyPolicyModal();

            return response.data;
        } else {
            throw new Error(response.message);
        }
    } catch (error) {
        logger.error("登录失败", error);
        throw error;
    }
}
```

### 3.2 Token 刷新

**后端伪代码**

```javascript
/**
 * 刷新访问Token
 * @param {string} refreshToken - 刷新令牌
 * @returns {object} 新Token
 */
function refreshToken(refreshToken) {
    let payload;
    try {
        payload = jwt.verify(refreshToken, JWT_SECRET);
    } catch (err) {
        if (err.name === "TokenExpiredError") {
            throw new BusinessError(4003, "登录已过期，请重新登录");
        }
        throw new BusinessError(4004, "登录状态无效");
    }

    if (payload.type !== "refresh") {
        throw new BusinessError(4004, "登录状态无效");
    }

    const user = await UserModel.findOne({ unionId: payload.unionId });
    if (!user) throw new BusinessError(4005, "用户不存在");

    const newToken = jwt.sign(
        { unionId: user.unionId, type: "access", iat: now() },
        JWT_SECRET,
        { expiresIn: "2h" }
    );

    await redis.setex(`token:${user.unionId}`, 7200, newToken);

    return { token: newToken, expiresIn: 7200 };
}
```

**前端伪代码**

```javascript
/**
 * 刷新Token
 * @returns {Promise<string>} 新accessToken
 */
async function refreshAccessToken() {
    const refreshToken = wx.getStorageSync("refresh_token");
    if (!refreshToken) throw new Error("无刷新令牌，需要重新登录");

    const response = await request.post("/api/v1/auth/refresh", { refreshToken });

    if (response.code === 0) {
        const { token, expiresIn } = response.data;
        wx.setStorageSync("access_token", token);
        wx.setStorageSync("token_expires", Date.now() + expiresIn * 1000);
        return token;
    } else {
        clearLoginState();
        throw new Error("登录已过期，请重新登录");
    }
}
```

---

## 4. AI 识别模块 API

### 4.1 照片上传

**接口信息**

| 属性 | 值 |
|------|-----|
| 接口名称 | 照片上传 |
| 接口路径 | POST /api/v1/upload/image |
| Content-Type | multipart/form-data |
| 是否需要认证 | 是 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| image | file | 是 | 图片文件，单张≤5MB |
| type | string | 是 | 用途类型: "diagnosis" |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| url | string | 图片访问URL |
| key | string | 对象存储Key |

**后端伪代码**

```javascript
/**
 * 上传图片到对象存储
 * @param {file} image - 图片文件
 * @param {string} type - 用途类型
 * @param {string} unionId - 用户标识
 * @returns {object} 上传结果
 */
function uploadImage(image, type, unionId) {
    // 1. 参数校验
    if (!image || !image.buffer) {
        throw new BusinessError(3001, "图片数据为空");
    }

    // 2. 文件大小校验
    const maxSize = 5 * 1024 * 1024;
    if (image.size > maxSize) {
        throw new BusinessError(3002, "图片大小超过5MB限制");
    }

    // 3. 文件类型校验
    const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!allowedTypes.includes(image.mimetype)) {
        throw new BusinessError(3003, "仅支持JPG/PNG格式");
    }

    // 4. 生成存储路径
    const date = formatDate(new Date(), "YYYY/MM/DD");
    const filename = `${generateUUID()}.${getExtension(image.mimetype)}`;
    const key = `images/${type}/${date}/${unionId}/${filename}`;

    // 5. 上传到腾讯云COS
    const cosResult = await cosClient.putObject({
        Bucket: COS_BUCKET,
        Region: COS_REGION,
        Key: key,
        Body: image.buffer,
        ContentType: image.mimetype,
        ServerSideEncryption: "AES256"
    });

    if (cosResult.statusCode !== 200) {
        logger.error("COS上传失败", { key, statusCode: cosResult.statusCode });
        throw new BusinessError(3004, "图片上传失败，请重试");
    }

    // 6. 记录上传日志
    await ImageUploadLog.create({
        unionId, key, size: image.size, type, uploadedAt: now()
    });

    // 7. 返回访问URL
    const url = `https://${COS_BUCKET}.cos.${COS_REGION}.myqcloud.com/${key}`;
    return { url, key };
}
```

**前端伪代码**

```javascript
/**
 * 上传单张图片
 * @param {string} tempFilePath - 本地临时文件路径
 * @returns {Promise<object>} 上传结果
 */
async function uploadImage(tempFilePath) {
    return new Promise((resolve, reject) => {
        wx.uploadFile({
            url: `${BASE_URL}/api/v1/upload/image`,
            filePath: tempFilePath,
            name: "image",
            formData: { type: "diagnosis" },
            header: { "Authorization": `Bearer ${getToken()}` },
            success: (res) => {
                const data = JSON.parse(res.data);
                if (data.code === 0) resolve(data.data);
                else reject(new Error(data.message));
            },
            fail: (err) => reject(new Error("上传失败: " + err.errMsg))
        });
    });
}

/**
 * 批量上传图片
 * @param {string[]} tempFilePaths - 本地临时文件路径数组
 * @returns {Promise<object[]>} 上传结果数组
 */
async function uploadImages(tempFilePaths) {
    const uploadTasks = tempFilePaths.map(path => uploadImage(path));
    return await Promise.all(uploadTasks);
}
```

### 4.2 AI 识别分析

**接口信息**

| 属性 | 值 |
|------|-----|
| 接口名称 | AI识别分析 |
| 接口路径 | POST /api/v1/diagnosis/analyze |
| 是否需要认证 | 是 |
| 超时时间 | 10秒 |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| imageUrls | array | 是 | 图片URL列表，1-3张 |
| bodyPart | string | 否 | 身体部位: face/trunk/limb/hand_foot/other |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| recordId | string | 识别记录ID |
| status | string | 状态: completed/pending/failed |
| result | object | 识别结果 |
| result.primary | object | 主要识别结果 |
| result.primary.diseaseId | string | 疾病ID |
| result.primary.diseaseName | string | 疾病名称 |
| result.primary.confidence | number | 置信度 0-1 |
| result.primary.description | string | 一句话说明 |
| result.primary.suggestedDepartment | string | 建议科室 |
| result.alternatives | array | 备选结果(最多2个) |
| result.urgencyLevel | string | 紧急程度: low/medium/high |
| result.disclaimer | string | 免责声明全文 |
| relatedArticles | array | 关联推荐文章 |

**后端伪代码**

```javascript
/**
 * AI识别分析主流程
 * @param {string[]} imageUrls - 图片URL列表
 * @param {string} bodyPart - 身体部位
 * @param {string} unionId - 用户标识
 * @returns {object} 识别结果
 */
async function analyzeDiagnosis(imageUrls, bodyPart, unionId) {
    // 1. 参数校验
    if (!imageUrls || imageUrls.length === 0) {
        throw new BusinessError(3101, "请至少上传1张照片");
    }
    if (imageUrls.length > 3) {
        throw new BusinessError(3102, "最多上传3张照片");
    }

    // 2. 创建识别记录(初始状态pending)
    const recordId = generateUUID();
    const record = await DiagnosisRecord.create({
        id: recordId,
        userId: unionId,
        images: imageUrls,
        bodyPart: bodyPart || "other",
        status: "pending",
        result: null,
        disclaimerAcknowledged: false,
        createdAt: now()
    });

    try {
        // 3. 调用AI识别服务
        const aiResult = await callAIRecognition(imageUrls, bodyPart);

        // 4. 解析识别结果
        const parsedResult = parseAIResult(aiResult);

        // 5. 查询关联科普文章
        const relatedArticles = await findRelatedArticles(parsedResult);

        // 6. 组装完整结果
        const finalResult = {
            primary: parsedResult.primary,
            alternatives: parsedResult.alternatives,
            urgencyLevel: parsedResult.urgencyLevel,
            disclaimer: getDisclaimerText()
        };

        // 7. 更新识别记录
        record.status = "completed";
        record.result = finalResult;
        await record.save();

        // 8. 返回结果
        return {
            recordId,
            status: "completed",
            result: finalResult,
            relatedArticles: relatedArticles.map(article => ({
                id: article.id,
                title: article.title,
                coverImage: article.coverImage
            }))
        };

    } catch (error) {
        logger.error("AI识别失败", { recordId, error: error.message, imageUrls });

        record.status = "failed";
        record.errorInfo = {
            message: error.message,
            code: error.code || "UNKNOWN",
            time: now()
        };
        await record.save();

        if (error.code === "AI_TIMEOUT") {
            throw new BusinessError(3103, "分析服务繁忙，请稍后重试");
        } else if (error.code === "LOW_QUALITY") {
            throw new BusinessError(3104, "照片不够清晰，建议重新拍摄后上传");
        } else {
            throw new BusinessError(3105, "分析失败，请稍后重试");
        }
    }
}

/**
 * 调用第三方AI识别服务
 * @param {string[]} imageUrls - 图片URL列表
 * @param {string} bodyPart - 身体部位
 * @returns {object} AI原始结果
 */
async function callAIRecognition(imageUrls, bodyPart) {
    const aiRequest = {
        images: imageUrls,
        bodyPart: bodyPart,
        requestId: generateUUID(),
        requireConfidence: true,
        topK: 3
    };

    const aiResponse = await httpClient.post(AI_SERVICE_URL, aiRequest, {
        timeout: 5000,
        headers: {
            "X-AI-API-Key": AI_API_KEY,
            "Content-Type": "application/json"
        }
    });

    if (aiResponse.status !== 200) {
        throw new ErrorWithCode("AI服务请求失败", "AI_REQUEST_FAILED");
    }

    return aiResponse.data;
}

/**
 * 解析AI识别结果
 * @param {object} aiResult - AI原始结果
 * @returns {object} 解析后的结果
 */
function parseAIResult(aiResult) {
    const predictions = aiResult.predictions || [];
    if (predictions.length === 0) {
        throw new ErrorWithCode("识别结果为空", "EMPTY_RESULT");
    }

    predictions.sort((a, b) => b.confidence - a.confidence);

    const topPrediction = predictions[0];
    const confidence = topPrediction.confidence;

    const diseaseInfo = await DiseaseModel.findOne({
        aiDiseaseId: topPrediction.diseaseId
    });

    const primary = {
        diseaseId: diseaseInfo?.id || topPrediction.diseaseId,
        diseaseName: diseaseInfo?.name || topPrediction.diseaseName,
        confidence: confidence,
        description: diseaseInfo?.briefDescription || "暂无详细说明",
        suggestedDepartment: diseaseInfo?.department || "皮肤科"
    };

    const alternatives = predictions
        .slice(1, 3)
        .filter(p => p.confidence >= 0.5)
        .map(p => ({
            diseaseId: p.diseaseId,
            diseaseName: p.diseaseName,
            confidence: p.confidence
        }));

    let urgencyLevel = "low";
    if (confidence < 0.5) {
        urgencyLevel = "high";
    } else if (diseaseInfo?.isUrgent) {
        urgencyLevel = "high";
    } else if (diseaseInfo?.needsAttention) {
        urgencyLevel = "medium";
    }

    return { primary, alternatives, urgencyLevel };
}

/**
 * 查询关联科普文章
 * @param {object} parsedResult - 解析后的识别结果
 * @returns {array} 关联文章列表
 */
async function findRelatedArticles(parsedResult) {
    const diseaseId = parsedResult.primary.diseaseId;

    let articles = await ArticleModel.find({
        relatedDiseases: diseaseId,
        reviewStatus: "published"
    })
    .sort({ views: -1, createdAt: -1 })
    .limit(3);

    if (articles.length < 3) {
        const diseaseInfo = await DiseaseModel.findOne({ id: diseaseId });
        const tags = diseaseInfo?.tags || [];

        const additionalArticles = await ArticleModel.find({
            tags: { $in: tags },
            reviewStatus: "published",
            id: { $nin: articles.map(a => a.id) }
        })
        .sort({ views: -1 })
        .limit(3 - articles.length);

        articles = articles.concat(additionalArticles);
    }

    return articles;
}

/**
 * 获取免责声明文本
 * @returns {string} 免责声明
 */
function getDisclaimerText() {
    return `⚠️ 重要提示

本识别结果由人工智能算法生成，仅供参考，不构成医疗诊断、治疗建议或用药指导。

皮肤病的诊断需要结合患者的病史、体格检查、实验室检查等多方面信息，仅凭图片识别存在局限性。

如您出现以下情况，请立即就医：
• 症状快速加重或扩散
• 伴有发热、疼痛剧烈
• 面部/生殖器部位出现症状
• 婴幼儿/孕妇/免疫力低下人群

本工具旨在帮助您初步了解皮肤症状，消除不必要的恐慌，但不能替代专业皮肤科医生的面诊。

点击"我已阅读并理解"即表示您知悉上述内容，并同意自行承担使用本工具的风险。`;
}
```

**前端伪代码**

```javascript
/**
 * 执行AI识别分析
 * @param {string[]} imageUrls - 已上传图片的URL列表
 * @param {string} bodyPart - 身体部位
 * @returns {Promise<object>} 识别结果
 */
async function analyzeDiagnosis(imageUrls, bodyPart = "other") {
    try {
        // 1. 显示分析中页面
        wx.navigateTo({ url: "/pages/analyzing/analyzing" });

        // 2. 调用分析接口
        const response = await request.post("/api/v1/diagnosis/analyze", {
            imageUrls, bodyPart
        });

        if (response.code === 0) {
            const { recordId, result, relatedArticles } = response.data;

            wx.redirectTo({
                url: `/pages/result/result?recordId=${recordId}`,
                success: () => {
                    eventBus.emit("diagnosisResult", {
                        result, relatedArticles
                    });
                }
            });

            return response.data;
        } else {
            throw new Error(response.message);
        }
    } catch (error) {
        wx.redirectTo({
            url: `/pages/result/result?error=${encodeURIComponent(error.message)}`
        });
        throw error;
    }
}
```

### 4.3 获取识别结果

**后端伪代码**

```javascript
/**
 * 获取识别结果
 * @param {string} recordId - 识别记录ID
 * @param {string} unionId - 当前用户标识
 * @returns {object} 识别结果
 */
async function getDiagnosisResult(recordId, unionId) {
    const record = await DiagnosisRecord.findOne({ id: recordId });

    if (!record) throw new BusinessError(3201, "识别记录不存在");

    if (record.userId !== unionId) {
        logger.warn("越权访问识别记录", {
            recordId, owner: record.userId, accessor: unionId
        });
        throw new BusinessError(3202, "无权查看该记录");
    }

    if (record.status === "pending") {
        return { recordId, status: "pending", message: "分析进行中，请稍候" };
    }

    if (record.status === "failed") {
        return {
            recordId, status: "failed",
            message: record.errorInfo?.message || "分析失败",
            errorCode: record.errorInfo?.code
        };
    }

    const relatedArticles = await findRelatedArticles(record.result);

    return {
        recordId, status: "completed",
        result: record.result,
        images: record.images,
        createdAt: record.createdAt,
        relatedArticles: relatedArticles.map(article => ({
            id: article.id, title: article.title, coverImage: article.coverImage
        }))
    };
}
```

### 4.4 确认免责声明

**后端伪代码**

```javascript
/**
 * 用户确认免责声明
 * @param {string} recordId - 识别记录ID
 * @param {string} unionId - 用户标识
 * @returns {object} 更新结果
 */
async function acknowledgeDisclaimer(recordId, unionId) {
    const record = await DiagnosisRecord.findOne({ id: recordId });
    if (!record) throw new BusinessError(3201, "识别记录不存在");
    if (record.userId !== unionId) throw new BusinessError(3202, "无权操作");

    record.disclaimerAcknowledged = true;
    record.acknowledgedAt = now();
    await record.save();

    return { success: true };
}
```

---

## 5. 科普内容模块 API

### 5.1 获取文章列表

**接口信息**

| 属性 | 值 |
|------|-----|
| 接口名称 | 获取文章列表 |
| 接口路径 | GET /api/v1/articles |
| 是否需要认证 | 否 |

**请求参数(Query)**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| category | string | 否 | 分类: by_location/by_type/seasonal |
| tag | string | 否 | 标签筛选 |
| keyword | string | 否 | 关键词搜索 |
| page | number | 否 | 页码，默认1 |
| pageSize | number | 否 | 每页数量，默认10，最大20 |

**后端伪代码**

```javascript
/**
 * 获取文章列表
 * @param {object} params - 查询参数
 * @returns {object} 文章列表及分页信息
 */
async function getArticleList(params) {
    const { category, tag, keyword, page = 1, pageSize = 10 } = params;

    // 1. 构建查询条件
    const query = { reviewStatus: "published" };

    if (category) query.category = category;
    if (tag) query.tags = tag;
    if (keyword) {
        query.$or = [
            { title: { $regex: keyword, $options: "i" } },
            { summary: { $regex: keyword, $options: "i" } },
            { content: { $regex: keyword, $options: "i" } }
        ];
    }

    // 2. 计算分页
    const skip = (page - 1) * pageSize;
    const limit = Math.min(pageSize, 20);

    // 3. 查询数据
    const [articles, total] = await Promise.all([
        ArticleModel.find(query)
            .sort({ isPinned: -1, views: -1, createdAt: -1 })
            .skip(skip)
            .limit(limit)
            .select("id title summary coverImage views author createdAt tags"),
        ArticleModel.countDocuments(query)
    ]);

    // 4. 组装响应
    return {
        list: articles,
        pagination: {
            page, pageSize: limit, total,
            hasMore: skip + articles.length < total
        }
    };
}
```

**前端伪代码**

```javascript
/**
 * 获取文章列表
 * @param {object} params - 查询参数
 * @returns {Promise<object>} 文章列表
 */
async function getArticles(params = {}) {
    const queryString = Object.keys(params)
        .map(k => `${k}=${encodeURIComponent(params[k])}`)
        .join("&");

    const response = await request.get(`/api/v1/articles?${queryString}`);
    if (response.code === 0) return response.data;
    throw new Error(response.message);
}
```

### 5.2 获取文章详情

**后端伪代码**

```javascript
/**
 * 获取文章详情
 * @param {string} articleId - 文章ID
 * @param {string} unionId - 当前用户标识(可选，用于收藏状态)
 * @returns {object} 文章详情
 */
async function getArticleDetail(articleId, unionId) {
    const article = await ArticleModel.findOne({
        id: articleId, reviewStatus: "published"
    });

    if (!article) throw new BusinessError(3301, "文章不存在或已下架");

    // 异步增加阅读数
    ArticleModel.updateOne(
        { id: articleId }, { $inc: { views: 1 } }
    ).catch(err => logger.error("更新阅读数失败", err));

    // 查询是否已收藏
    let isFavorited = false;
    if (unionId) {
        const favorite = await FavoriteModel.findOne({
            userId: unionId, articleId: articleId
        });
        isFavorited = !!favorite;
    }

    // 查询相关推荐
    const relatedArticles = await ArticleModel.find({
        tags: { $in: article.tags },
        id: { $ne: articleId },
        reviewStatus: "published"
    })
    .sort({ views: -1 })
    .limit(3)
    .select("id title coverImage");

    return {
        id: article.id,
        title: article.title,
        summary: article.summary,
        coverImage: article.coverImage,
        content: article.content,
        author: article.author,
        reviewer: article.reviewer,
        views: article.views + 1,
        createdAt: article.createdAt,
        updatedAt: article.updatedAt,
        tags: article.tags,
        isFavorited,
        relatedArticles
    };
}
```

**前端伪代码**

```javascript
/**
 * 获取文章详情
 * @param {string} articleId - 文章ID
 * @returns {Promise<object>} 文章详情
 */
async function getArticleDetail(articleId) {
    const response = await request.get(`/api/v1/articles/${articleId}`);
    if (response.code === 0) return response.data;
    throw new Error(response.message);
}
```

### 5.3 搜索文章

**后端伪代码**

```javascript
/**
 * 搜索文章
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {object} 搜索结果
 */
async function searchArticles(keyword, page = 1, pageSize = 10) {
    if (!keyword || keyword.trim().length === 0) {
        throw new BusinessError(3302, "请输入搜索关键词");
    }
    if (keyword.length > 50) {
        throw new BusinessError(3303, "关键词过长");
    }

    const cleanKeyword = filterSensitiveWords(keyword.trim());

    const query = {
        reviewStatus: "published",
        $or: [
            { title: { $regex: cleanKeyword, $options: "i" } },
            { summary: { $regex: cleanKeyword, $options: "i" } },
            { tags: cleanKeyword }
        ]
    };

    const skip = (page - 1) * pageSize;
    const [articles, total] = await Promise.all([
        ArticleModel.find(query)
            .sort({ title: { $regex: cleanKeyword } ? -1 : 0, views: -1 })
            .skip(skip)
            .limit(pageSize)
            .select("id title summary coverImage views tags"),
        ArticleModel.countDocuments(query)
    ]);

    // 无结果时返回推荐
    let recommendations = [];
    if (articles.length === 0) {
        recommendations = await ArticleModel.find({ reviewStatus: "published" })
            .sort({ views: -1 })
            .limit(5)
            .select("id title coverImage");
    }

    // 记录搜索日志
    await SearchLog.create({
        keyword: cleanKeyword, resultCount: total, timestamp: now()
    });

    return {
        list: articles,
        pagination: { page, pageSize, total, hasMore: skip + articles.length < total },
        recommendations
    };
}
```

---

## 6. 用户中心模块 API

### 6.1 获取用户信息

**接口信息**

| 属性 | 值 |
|------|-----|
| 接口名称 | 获取用户信息 |
| 接口路径 | GET /api/v1/user/profile |
| 是否需要认证 | 是 |

**后端伪代码**

```javascript
/**
 * 获取用户信息
 * @param {string} unionId - 用户标识
 * @returns {object} 用户信息
 */
async function getUserProfile(unionId) {
    const user = await UserModel.findOne({ unionId });
    if (!user) throw new BusinessError(3401, "用户不存在");

    const diagnosisCount = await DiagnosisRecord.countDocuments({
        userId: unionId, status: "completed"
    });

    const favoriteCount = await FavoriteModel.countDocuments({
        userId: unionId
    });

    return {
        unionId: user.unionId,
        nickName: user.nickName,
        avatarUrl: user.avatarUrl,
        createdAt: user.createdAt,
        diagnosisCount,
        favoriteCount
    };
}
```

### 6.2 获取识别历史

**后端伪代码**

```javascript
/**
 * 获取用户识别历史
 * @param {string} unionId - 用户标识
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {object} 历史记录列表
 */
async function getUserHistory(unionId, page = 1, pageSize = 20) {
    const skip = (page - 1) * pageSize;

    const [records, total] = await Promise.all([
        DiagnosisRecord.find({ userId: unionId })
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(pageSize)
            .select("id images result status createdAt"),
        DiagnosisRecord.countDocuments({ userId: unionId })
    ]);

    const list = records.map(record => ({
        recordId: record.id,
        thumbnail: record.images[0],
        diseaseName: record.result?.primary?.diseaseName || "无法判断",
        confidence: record.result?.primary?.confidence || 0,
        status: record.status,
        createdAt: record.createdAt
    }));

    return {
        list,
        pagination: { page, pageSize, total, hasMore: skip + records.length < total }
    };
}
```

**前端伪代码**

```javascript
/**
 * 获取识别历史
 * @param {number} page - 页码
 * @returns {Promise<object>} 历史记录
 */
async function getHistory(page = 1) {
    const response = await request.get(`/api/v1/user/history?page=${page}`);
    if (response.code === 0) return response.data;
    throw new Error(response.message);
}
```

### 6.3 收藏管理

**添加收藏后端伪代码**

```javascript
/**
 * 添加收藏
 * @param {string} unionId - 用户标识
 * @param {string} articleId - 文章ID
 * @returns {object} 收藏结果
 */
async function addFavorite(unionId, articleId) {
    const article = await ArticleModel.findOne({
        id: articleId, reviewStatus: "published"
    });
    if (!article) throw new BusinessError(3501, "文章不存在或已下架");

    const existing = await FavoriteModel.findOne({
        userId: unionId, articleId
    });
    if (existing) throw new BusinessError(3502, "已收藏该文章");

    await FavoriteModel.create({
        id: generateUUID(), userId: unionId, articleId, createdAt: now()
    });

    return { success: true };
}
```

**取消收藏后端伪代码**

```javascript
/**
 * 取消收藏
 * @param {string} unionId - 用户标识
 * @param {string} articleId - 文章ID
 * @returns {object} 操作结果
 */
async function removeFavorite(unionId, articleId) {
    const result = await FavoriteModel.deleteOne({
        userId: unionId, articleId
    });
    if (result.deletedCount === 0) {
        throw new BusinessError(3503, "未收藏该文章");
    }
    return { success: true };
}
```

**获取收藏列表后端伪代码**

```javascript
/**
 * 获取用户收藏列表
 * @param {string} unionId - 用户标识
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 * @returns {object} 收藏列表
 */
async function getUserFavorites(unionId, page = 1, pageSize = 20) {
    const skip = (page - 1) * pageSize;

    const favorites = await FavoriteModel.aggregate([
        { $match: { userId: unionId } },
        { $sort: { createdAt: -1 } },
        { $skip: skip },
        { $limit: pageSize },
        {
            $lookup: {
                from: "articles",
                localField: "articleId",
                foreignField: "id",
                as: "article"
            }
        },
        { $unwind: "$article" }
    ]);

    const list = favorites.map(fav => ({
        favoriteId: fav.id,
        articleId: fav.article.id,
        title: fav.article.title,
        summary: fav.article.summary,
        coverImage: fav.article.coverImage,
        author: fav.article.author,
        createdAt: fav.createdAt,
        isAvailable: fav.article.reviewStatus === "published"
    }));

    const total = await FavoriteModel.countDocuments({ userId: unionId });

    return {
        list,
        pagination: { page, pageSize, total, hasMore: skip + favorites.length < total }
    };
}
```

**前端收藏服务伪代码**

```javascript
/**
 * 收藏管理
 */
const favoriteService = {
    async add(articleId) {
        const response = await request.post("/api/v1/user/favorites", { articleId });
        return response.data;
    },

    async remove(articleId) {
        const response = await request.delete(`/api/v1/user/favorites/${articleId}`);
        return response.data;
    },

    async getList(page = 1) {
        const response = await request.get(`/api/v1/user/favorites?page=${page}`);
        return response.data;
    },

    async toggle(articleId, isFavorited) {
        if (isFavorited) return this.remove(articleId);
        else return this.add(articleId);
    }
};
```

### 6.4 删除识别记录

**后端伪代码**

```javascript
/**
 * 删除识别记录
 * @param {string} unionId - 用户标识
 * @param {string} recordId - 记录ID
 * @returns {object} 操作结果
 */
async function deleteHistoryRecord(unionId, recordId) {
    const record = await DiagnosisRecord.findOne({ id: recordId });
    if (!record) throw new BusinessError(3601, "记录不存在");
    if (record.userId !== unionId) throw new BusinessError(3602, "无权删除该记录");

    // 删除关联的图片文件
    if (record.images && record.images.length > 0) {
        for (const imageUrl of record.images) {
            const key = extractKeyFromUrl(imageUrl);
            if (key) {
                cosClient.deleteObject({
                    Bucket: COS_BUCKET, Region: COS_REGION, Key: key
                }).catch(err => logger.error("删除COS文件失败", err));
            }
        }
    }

    await DiagnosisRecord.deleteOne({ id: recordId });
    return { success: true };
}
```

---

## 7. 后端服务伪代码

### 7.1 主服务入口

```javascript
/**
 * SkinCheck 后端服务主入口
 */
const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");

const app = express();

// 1. 安全中间件
app.use(helmet());
app.use(cors({
    origin: ["https://servicewechat.com"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization", "X-Request-ID"]
}));

// 2. 限流配置
const limiter = rateLimit({
    windowMs: 60 * 1000,
    max: 100,
    message: { code: 429, message: "请求过于频繁，请稍后再试" }
});
app.use(limiter);

// 3. 认证接口单独限流
const authLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 10,
    message: { code: 429, message: "登录尝试过于频繁" }
});

// 4. 请求解析
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true }));

// 5. 请求追踪
app.use((req, res, next) => {
    req.requestId = req.headers["x-request-id"] || generateUUID();
    res.setHeader("X-Request-ID", req.requestId);
    logger.info("请求开始", {
        requestId: req.requestId,
        method: req.method,
        path: req.path,
        ip: req.ip
    });
    next();
});

// 6. 路由注册
app.use("/api/v1/auth", authLimiter, authRoutes);
app.use("/api/v1/upload", authenticate, uploadRoutes);
app.use("/api/v1/diagnosis", authenticate, diagnosisRoutes);
app.use("/api/v1/articles", articleRoutes);
app.use("/api/v1/user", authenticate, userRoutes);

// 7. 健康检查
app.get("/health", (req, res) => {
    res.json({ status: "ok", timestamp: now() });
});

// 8. 全局错误处理
app.use(errorHandler);

// 9. 启动服务
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    logger.info(`SkinCheck服务启动，端口: ${PORT}`);
});
```

### 7.2 认证中间件

```javascript
/**
 * JWT认证中间件
 */
function authenticate(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({
            code: 4101,
            message: "请先登录",
            requestId: req.requestId
        });
    }

    const token = authHeader.substring(7);

    try {
        // 验证Token
        const payload = jwt.verify(token, JWT_SECRET);

        // 校验Token类型
        if (payload.type !== "access") {
            throw new Error("Invalid token type");
        }

        // 检查Redis中是否存在(支持后端强制登出)
        const cachedToken = await redis.get(`token:${payload.unionId}`);
        if (!cachedToken || cachedToken !== token) {
            throw new Error("Token invalidated");
        }

        // 将用户信息附加到请求
        req.user = {
            unionId: payload.unionId,
            iat: payload.iat
        };

        next();
    } catch (err) {
        if (err.name === "TokenExpiredError") {
            return res.status(401).json({
                code: 4102,
                message: "登录已过期，请重新登录",
                requestId: req.requestId
            });
        }

        return res.status(401).json({
            code: 4103,
            message: "登录状态无效",
            requestId: req.requestId
        });
    }
}
```

### 7.3 全局错误处理

```javascript
/**
 * 全局错误处理中间件
 */
function errorHandler(err, req, res, next) {
    const requestId = req.requestId || "unknown";

    // 业务错误
    if (err instanceof BusinessError) {
        logger.warn("业务错误", {
            requestId,
            code: err.code,
            message: err.message,
            path: req.path
        });

        return res.status(200).json({
            code: err.code,
            message: err.message,
            requestId
        });
    }

    // 未预期的错误
    logger.error("系统错误", {
        requestId,
        error: err.message,
        stack: err.stack,
        path: req.path,
        body: req.body
    });

    return res.status(500).json({
        code: 5000,
        message: "系统繁忙，请稍后重试",
        requestId
    });
}

/**
 * 业务错误类
 */
class BusinessError extends Error {
    constructor(code, message) {
        super(message);
        this.code = code;
        this.name = "BusinessError";
    }
}
```

---

## 8. 前端服务层伪代码

### 8.1 网络请求封装

```javascript
/**
 * 网络请求封装
 */
const request = {
    BASE_URL: "https://api.skincheck.example.com",
    TIMEOUT: 10000,

    getToken() {
        return wx.getStorageSync("access_token");
    },

    isTokenExpiring() {
        const expires = wx.getStorageSync("token_expires");
        if (!expires) return true;
        return Date.now() > expires - 5 * 60 * 1000;
    },

    async send(options) {
        // Token即将过期，先刷新
        if (this.isTokenExpiring() && !options.url.includes("/auth/")) {
            try { await refreshAccessToken(); } catch (e) {}
        }

        return new Promise((resolve, reject) => {
            const token = this.getToken();

            wx.request({
                url: `${this.BASE_URL}${options.url}`,
                method: options.method || "GET",
                data: options.data,
                header: {
                    "Content-Type": "application/json",
                    "Authorization": token ? `Bearer ${token}` : "",
                    "X-Request-ID": generateUUID(),
                    "X-Client-Version": "1.0.0",
                    ...options.headers
                },
                timeout: options.timeout || this.TIMEOUT,
                success: (res) => {
                    if (res.statusCode === 401) {
                        clearLoginState();
                        wx.showModal({
                            title: "登录过期",
                            content: "您的登录已过期，请重新登录",
                            showCancel: false,
                            success: () => {
                                wx.navigateTo({ url: "/pages/login/login" });
                            }
                        });
                        reject(new Error("登录已过期"));
                        return;
                    }

                    if (res.statusCode >= 500) {
                        reject(new Error("服务器繁忙，请稍后重试"));
                        return;
                    }

                    const data = res.data;
                    if (data.code !== 0) {
                        reject(new Error(data.message || "请求失败"));
                        return;
                    }

                    resolve(data);
                },
                fail: (err) => {
                    if (err.errMsg.includes("timeout")) {
                        reject(new Error("请求超时，请检查网络"));
                    } else if (err.errMsg.includes("fail")) {
                        reject(new Error("网络连接失败，请检查网络设置"));
                    } else {
                        reject(new Error(err.errMsg));
                    }
                }
            });
        });
    },

    get(url, params = {}) {
        const queryString = Object.keys(params)
            .map(k => `${k}=${encodeURIComponent(params[k])}`)
            .join("&");
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.send({ url: fullUrl, method: "GET" });
    },

    post(url, data = {}) {
        return this.send({ url, method: "POST", data });
    },

    delete(url) {
        return this.send({ url, method: "DELETE" });
    }
};
```

### 8.2 认证状态管理

```javascript
/**
 * 认证状态管理
 */
const authManager = {
    isLoggedIn() {
        const token = wx.getStorageSync("access_token");
        const expires = wx.getStorageSync("token_expires");
        if (!token || !expires) return false;
        return Date.now() < expires;
    },

    getCurrentUser() {
        return wx.getStorageSync("user_info");
    },

    clearLoginState() {
        wx.removeStorageSync("access_token");
        wx.removeStorageSync("refresh_token");
        wx.removeStorageSync("token_expires");
        wx.removeStorageSync("user_info");
    },

    requireLogin(redirectUrl = "") {
        if (!this.isLoggedIn()) {
            wx.navigateTo({
                url: `/pages/login/login?redirect=${encodeURIComponent(redirectUrl)}`
            });
            return false;
        }
        return true;
    }
};
```

### 8.3 页面级服务封装

```javascript
/**
 * 首页服务
 */
const homeService = {
    async getHomeData() {
        const [bannerRes, articlesRes] = await Promise.all([
            request.get("/api/v1/articles", { category: "seasonal", pageSize: 5 }),
            request.get("/api/v1/articles", { pageSize: 10 })
        ]);

        return {
            banners: bannerRes.data.list,
            articles: articlesRes.data.list,
            hasMore: articlesRes.data.pagination.hasMore
        };
    }
};

/**
 * 识别服务
 */
const diagnosisService = {
    async performDiagnosis(tempFilePaths, bodyPart) {
        const uploadedImages = await uploadImages(tempFilePaths);
        const imageUrls = uploadedImages.map(img => img.url);
        return await analyzeDiagnosis(imageUrls, bodyPart);
    }
};
```

---

## 9. 数据模型定义

### 9.1 MongoDB Schema 定义

```javascript
/**
 * 用户模型
 */
const UserSchema = new mongoose.Schema({
    unionId: { 
        type: String, 
        required: true, 
        unique: true, 
        index: true 
    },
    openId: { 
        type: String, 
        required: true 
    },
    nickName: { 
        type: String, 
        default: "微信用户" 
    },
    avatarUrl: { 
        type: String, 
        default: "" 
    },
    createdAt: { 
        type: Date, 
        default: Date.now 
    },
    lastLoginAt: { 
        type: Date, 
        default: Date.now 
    }
});

/**
 * 识别记录模型
 */
const DiagnosisRecordSchema = new mongoose.Schema({
    id: { 
        type: String, 
        required: true, 
        unique: true 
    },
    userId: { 
        type: String, 
        required: true, 
        index: true 
    },
    images: [{ 
        type: String 
    }],
    bodyPart: { 
        type: String, 
        enum: ["face", "trunk", "limb", "hand_foot", "other"],
        default: "other"
    },
    status: { 
        type: String, 
        enum: ["pending", "completed", "failed"],
        default: "pending"
    },
    result: {
        primary: {
            diseaseId: String,
            diseaseName: String,
            confidence: Number,
            description: String,
            suggestedDepartment: String
        },
        alternatives: [{
            diseaseId: String,
            diseaseName: String,
            confidence: Number
        }],
        urgencyLevel: { 
            type: String, 
            enum: ["low", "medium", "high"] 
        },
        disclaimer: String
    },
    disclaimerAcknowledged: { 
        type: Boolean, 
        default: false 
    },
    acknowledgedAt: Date,
    errorInfo: {
        message: String,
        code: String,
        time: Date
    },
    createdAt: { 
        type: Date, 
        default: Date.now,
        index: true 
    }
});

/**
 * 文章模型
 */
const ArticleSchema = new mongoose.Schema({
    id: { 
        type: String, 
        required: true, 
        unique: true 
    },
    title: { 
        type: String, 
        required: true 
    },
    summary: { 
        type: String, 
        required: true 
    },
    coverImage: { 
        type: String 
    },
    content: { 
        type: String, 
        required: true 
    },
    category: { 
        type: String, 
        enum: ["by_location", "by_type", "seasonal"] 
    },
    tags: [{ 
        type: String 
    }],
    relatedDiseases: [{ 
        type: String 
    }],
    views: { 
        type: Number, 
        default: 0 
    },
    author: { 
        type: String, 
        required: true 
    },
    reviewer: { 
        type: String 
    },
    reviewStatus: { 
        type: String, 
        enum: ["draft", "reviewed", "published"],
        default: "draft"
    },
    isPinned: { 
        type: Boolean, 
        default: false 
    },
    createdAt: { 
        type: Date, 
        default: Date.now 
    },
    updatedAt: { 
        type: Date, 
        default: Date.now 
    }
});

/**
 * 收藏模型
 */
const FavoriteSchema = new mongoose.Schema({
    id: { 
        type: String, 
        required: true, 
        unique: true 
    },
    userId: { 
        type: String, 
        required: true, 
        index: true 
    },
    articleId: { 
        type: String, 
        required: true 
    },
    createdAt: { 
        type: Date, 
        default: Date.now 
    }
});

// 复合唯一索引：用户不能重复收藏同一文章
FavoriteSchema.index({ userId: 1, articleId: 1 }, { unique: true });

/**
 * 疾病知识库模型
 */
const DiseaseSchema = new mongoose.Schema({
    id: { 
        type: String, 
        required: true, 
        unique: true 
    },
    aiDiseaseId: { 
        type: String, 
        index: true 
    },
    name: { 
        type: String, 
        required: true 
    },
    briefDescription: String,
    department: { 
        type: String, 
        default: "皮肤科" 
    },
    isUrgent: { 
        type: Boolean, 
        default: false 
    },
    needsAttention: { 
        type: Boolean, 
        default: false 
    },
    tags: [{ 
        type: String 
    }],
    symptoms: [{ 
        type: String 
    }],
    createdAt: { 
        type: Date, 
        default: Date.now 
    }
});
```

---

## 10. 错误码表

### 10.1 全局错误码

| 错误码 | 错误信息 | 说明 |
|--------|---------|------|
| 0 | success | 请求成功 |
| 4000 | 参数错误 | 通用参数校验失败 |
| 4001 | 登录凭证无效 | code为空或格式错误 |
| 4002 | 微信登录失败 | 微信接口返回错误 |
| 4003 | 登录已过期 | refreshToken过期 |
| 4004 | 登录状态无效 | Token验证失败 |
| 4005 | 用户不存在 | 查询不到用户记录 |
| 4101 | 请先登录 | 未提供Token |
| 4102 | 登录已过期，请重新登录 | accessToken过期 |
| 4103 | 登录状态无效 | Token被篡改或类型错误 |
| 429 | 请求过于频繁 | 触发限流 |
| 5000 | 系统繁忙，请稍后重试 | 未预期的系统错误 |

### 10.2 上传模块错误码

| 错误码 | 错误信息 | 说明 |
|--------|---------|------|
| 3001 | 图片数据为空 | 未提供文件 |
| 3002 | 图片大小超过5MB限制 | 文件过大 |
| 3003 | 仅支持JPG/PNG格式 | 格式不支持 |
| 3004 | 图片上传失败，请重试 | COS上传失败 |

### 10.3 识别模块错误码

| 错误码 | 错误信息 | 说明 |
|--------|---------|------|
| 3101 | 请至少上传1张照片 | 图片数量不足 |
| 3102 | 最多上传3张照片 | 图片数量超限 |
| 3103 | 分析服务繁忙，请稍后重试 | AI服务超时 |
| 3104 | 照片不够清晰，建议重新拍摄后上传 | 照片质量不足 |
| 3105 | 分析失败，请稍后重试 | 其他AI错误 |
| 3201 | 识别记录不存在 | 记录ID无效 |
| 3202 | 无权查看该记录 | 越权访问 |

### 10.4 文章模块错误码

| 错误码 | 错误信息 | 说明 |
|--------|---------|------|
| 3301 | 文章不存在或已下架 | 文章ID无效或未发布 |
| 3302 | 请输入搜索关键词 | 关键词为空 |
| 3303 | 关键词过长 | 超过50字符 |

### 10.5 用户模块错误码

| 错误码 | 错误信息 | 说明 |
|--------|---------|------|
| 3401 | 用户不存在 | 查询不到用户 |
| 3501 | 文章不存在或已下架 | 收藏时文章无效 |
| 3502 | 已收藏该文章 | 重复收藏 |
| 3503 | 未收藏该文章 | 取消收藏时未找到 |
| 3601 | 记录不存在 | 删除历史时记录无效 |
| 3602 | 无权删除该记录 | 越权删除 |

---

## 11. 接口调用时序图

### 11.1 完整识别流程

```
用户        小程序前端        后端服务        腾讯云COS      AI识别服务
 |             |                |               |              |
 |--拍照选图-->|                |               |              |
 |             |--上传图片---->|               |              |
 |             |               |--存储文件---->|              |
 |             |               |<--返回URL-----|              |
 |             |<--上传成功----|               |              |
 |             |--提交分析---->|               |              |
 |             |               |--创建记录---->|              |
 |             |               |--调用AI识别------------------->|
 |             |               |<--返回结果---------------------|
 |             |               |--查询关联文章                |
 |             |               |--更新记录                    |
 |             |<--返回结果----|               |              |
 |<--展示结果--|                |               |              |
 |--滚动声明-->|                |               |              |
 |--点击确认-->|                |               |              |
 |             |--确认声明---->|               |              |
 |             |               |--更新确认状态                |
 |             |<--确认成功----|               |              |
 |<--解锁结果--|                |               |              |
```

### 11.2 文章浏览流程

```
用户        小程序前端        后端服务        数据库
 |             |                |               |
 |--打开首页-->|                |               |
 |             |--请求列表---->|               |
 |             |               |--查询文章------>|
 |             |               |<--返回数据------|
 |             |<--返回列表----|               |
 |<--展示文章--|                |               |
 |--点击文章-->|                |               |
 |             |--请求详情---->|               |
 |             |               |--查询详情------>|
 |             |               |--更新阅读数---->|
 |             |               |<--返回详情------|
 |             |<--返回数据----|               |
 |<--展示详情--|                |               |
```

---

> **文档维护**：本 API 文档为活文档，接口变更需同步更新版本号并通知前后端团队。

