const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const DiagnosisRecord = require('../models/DiagnosisRecord');
const Article = require('../models/Article');
const Disease = require('../models/Disease');
const { BusinessError, ErrorWithCode } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL;
const AI_API_KEY = process.env.AI_API_KEY;

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

async function callAIRecognition(imageUrls, bodyPart) {
    const aiRequest = {
        images: imageUrls,
        bodyPart: bodyPart,
        requestId: uuidv4(),
        requireConfidence: true,
        topK: 3
    };

    try {
        const aiResponse = await axios.post(AI_SERVICE_URL, aiRequest, {
            timeout: 5000,
            headers: {
                'X-AI-API-Key': AI_API_KEY,
                'Content-Type': 'application/json'
            }
        });

        if (aiResponse.status !== 200) {
            throw new ErrorWithCode('AI服务请求失败', 'AI_REQUEST_FAILED');
        }

        return aiResponse.data;
    } catch (error) {
        if (error.code === 'ECONNABORTED') {
            throw new ErrorWithCode('AI识别超时', 'AI_TIMEOUT');
        }
        throw new ErrorWithCode('AI服务异常', 'AI_SERVICE_ERROR');
    }
}

async function parseAIResult(aiResult) {
    const predictions = aiResult.predictions || [];
    
    if (predictions.length === 0) {
        throw new ErrorWithCode('识别结果为空', 'EMPTY_RESULT');
    }

    predictions.sort((a, b) => b.confidence - a.confidence);

    const topPrediction = predictions[0];
    const confidence = topPrediction.confidence;

    const diseaseInfo = await Disease.findOne({
        aiDiseaseId: topPrediction.diseaseId
    });

    const primary = {
        diseaseId: diseaseInfo?.id || topPrediction.diseaseId,
        diseaseName: diseaseInfo?.name || topPrediction.diseaseName,
        confidence: confidence,
        description: diseaseInfo?.briefDescription || '暂无详细说明',
        suggestedDepartment: diseaseInfo?.department || '皮肤科'
    };

    const alternatives = predictions
        .slice(1, 3)
        .filter(p => p.confidence >= 0.5)
        .map(p => ({
            diseaseId: p.diseaseId,
            diseaseName: p.diseaseName,
            confidence: p.confidence
        }));

    let urgencyLevel = 'low';
    if (confidence < 0.5) {
        urgencyLevel = 'high';
    } else if (diseaseInfo?.isUrgent) {
        urgencyLevel = 'high';
    } else if (diseaseInfo?.needsAttention) {
        urgencyLevel = 'medium';
    }

    return { primary, alternatives, urgencyLevel };
}

async function findRelatedArticles(parsedResult) {
    const diseaseId = parsedResult.primary.diseaseId;

    let articles = await Article.find({
        relatedDiseases: diseaseId,
        reviewStatus: 'published'
    })
    .sort({ views: -1, createdAt: -1 })
    .limit(3);

    if (articles.length < 3) {
        const diseaseInfo = await Disease.findOne({ id: diseaseId });
        const tags = diseaseInfo?.tags || [];

        const additionalArticles = await Article.find({
            tags: { $in: tags },
            reviewStatus: 'published',
            id: { $nin: articles.map(a => a.id) }
        })
        .sort({ views: -1 })
        .limit(3 - articles.length);

        articles = articles.concat(additionalArticles);
    }

    return articles;
}

async function analyzeDiagnosis(req, res, next) {
    try {
        const { imageUrls, bodyPart } = req.body;
        const unionId = req.user.unionId;

        if (!imageUrls || imageUrls.length === 0) {
            throw new BusinessError(3101, '请至少上传1张照片');
        }
        if (imageUrls.length > 3) {
            throw new BusinessError(3102, '最多上传3张照片');
        }

        const recordId = uuidv4();
        const record = await DiagnosisRecord.create({
            id: recordId,
            userId: unionId,
            images: imageUrls,
            bodyPart: bodyPart || 'other',
            status: 'pending',
            result: null,
            disclaimerAcknowledged: false,
            createdAt: new Date()
        });

        try {
            const aiResult = await callAIRecognition(imageUrls, bodyPart);
            const parsedResult = await parseAIResult(aiResult);
            const relatedArticles = await findRelatedArticles(parsedResult);

            const finalResult = {
                primary: parsedResult.primary,
                alternatives: parsedResult.alternatives,
                urgencyLevel: parsedResult.urgencyLevel,
                disclaimer: getDisclaimerText()
            };

            record.status = 'completed';
            record.result = finalResult;
            await record.save();

            res.json({
                code: 0,
                message: 'success',
                data: {
                    recordId,
                    status: 'completed',
                    result: finalResult,
                    relatedArticles: relatedArticles.map(article => ({
                        id: article.id,
                        title: article.title,
                        coverImage: article.coverImage
                    }))
                },
                requestId: req.headers['x-request-id'] || uuidv4()
            });
        } catch (error) {
            logger.error('AI识别失败', { recordId, error: error.message, imageUrls });

            record.status = 'failed';
            record.errorInfo = {
                message: error.message,
                code: error.code || 'UNKNOWN',
                time: new Date()
            };
            await record.save();

            if (error.code === 'AI_TIMEOUT') {
                throw new BusinessError(3103, '分析服务繁忙，请稍后重试');
            } else if (error.code === 'LOW_QUALITY') {
                throw new BusinessError(3104, '照片不够清晰，建议重新拍摄后上传');
            } else {
                throw new BusinessError(3105, '分析失败，请稍后重试');
            }
        }
    } catch (error) {
        next(error);
    }
}

async function getDiagnosisRecord(req, res, next) {
    try {
        const { recordId } = req.params;
        const unionId = req.user.unionId;

        const record = await DiagnosisRecord.findOne({ id: recordId });
        
        if (!record) {
            throw new BusinessError(3201, '记录不存在');
        }

        if (record.userId !== unionId) {
            throw new BusinessError(3202, '无权查看该记录');
        }

        res.json({
            code: 0,
            message: 'success',
            data: record,
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

module.exports = {
    analyzeDiagnosis,
    getDiagnosisRecord
};
