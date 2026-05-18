const { request, uploadFile } = require('../utils/request');

async function uploadImages(tempFilePaths) {
    const uploadTasks = tempFilePaths.map(path => 
        uploadFile(path, { type: 'diagnosis' })
    );
    return await Promise.all(uploadTasks);
}

async function analyzeDiagnosis(imageUrls, bodyPart = 'other') {
    const response = await request({
        url: `${getApp().globalData.baseUrl}/diagnosis/analyze`,
        method: 'POST',
        data: { imageUrls, bodyPart },
        timeout: 15000
    });

    if (response.code === 0) {
        return response.data;
    } else {
        throw new Error(response.message);
    }
}

async function getDiagnosisRecord(recordId) {
    const response = await request({
        url: `${getApp().globalData.baseUrl}/diagnosis/record/${recordId}`,
        method: 'GET'
    });

    if (response.code === 0) {
        return response.data;
    } else {
        throw new Error(response.message);
    }
}

module.exports = {
    uploadImages,
    analyzeDiagnosis,
    getDiagnosisRecord
};
