const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const ImageUploadLogSchema = new Schema({
    unionId: { type: String, required: true },
    key: { type: String, required: true },
    size: { type: Number },
    type: { type: String },
    uploadedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('ImageUploadLog', ImageUploadLogSchema);
