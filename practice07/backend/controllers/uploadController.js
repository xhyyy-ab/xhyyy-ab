const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const ImageUploadLog = require('../models/ImageUploadLog');
const { BusinessError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

const storage = multer.memoryStorage();

const fileFilter = (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    
    if (!allowedTypes.includes(file.mimetype)) {
        return cb(new BusinessError(3003, '仅支持JPG/PNG格式'), false);
    }
    
    cb(null, true);
};

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 5 * 1024 * 1024
    },
    fileFilter: fileFilter
});

async function uploadImage(req, res, next) {
    try {
        if (!req.file) {
            throw new BusinessError(3001, '图片数据为空');
        }

        const unionId = req.user.unionId;
        const type = req.body.type || 'diagnosis';
        const file = req.file;

        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        
        const ext = path.extname(file.originalname) || '.jpg';
        const filename = `${uuidv4()}${ext}`;
        const key = `images/${type}/${year}/${month}/${day}/${unionId}/${filename}`;

        const url = `https://${process.env.COS_BUCKET}.cos.${process.env.COS_REGION}.myqcloud.com/${key}`;

        await ImageUploadLog.create({
            unionId,
            key,
            size: file.size,
            type,
            uploadedAt: new Date()
        });

        logger.info('图片上传成功', { unionId, key, size: file.size });

        res.json({
            code: 0,
            message: 'success',
            data: {
                url,
                key
            },
            requestId: req.headers['x-request-id'] || uuidv4()
        });
    } catch (error) {
        next(error);
    }
}

module.exports = {
    upload,
    uploadImage
};
