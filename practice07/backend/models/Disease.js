const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const DiseaseSchema = new Schema({
    id: { type: String, required: true, unique: true },
    aiDiseaseId: { type: String },
    name: { type: String, required: true },
    briefDescription: { type: String },
    department: { type: String, default: '皮肤科' },
    tags: [{ type: String }],
    isUrgent: { type: Boolean, default: false },
    needsAttention: { type: Boolean, default: false }
});

module.exports = mongoose.model('Disease', DiseaseSchema);
