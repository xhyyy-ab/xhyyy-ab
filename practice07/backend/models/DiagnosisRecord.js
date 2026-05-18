const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DiagnosisRecordSchema = new Schema({
    id: { type: String, required: true, unique: true },
    userId: { type: String, required: true, index: true },
    images: [{ type: String }],
    bodyPart: { type: String, default: 'other' },
    status: { 
        type: String, 
        enum: ['pending', 'completed', 'failed'],
        default: 'pending'
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
            enum: ['low', 'medium', 'high']
        },
        disclaimer: String
    },
    errorInfo: {
        message: String,
        code: String,
        time: Date
    },
    disclaimerAcknowledged: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now, index: true }
});

module.exports = mongoose.model('DiagnosisRecord', DiagnosisRecordSchema);
