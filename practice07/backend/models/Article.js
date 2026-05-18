const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const ArticleSchema = new Schema({
    id: { type: String, required: true, unique: true },
    title: { type: String, required: true },
    summary: { type: String },
    coverImage: { type: String },
    content: { type: String },
    category: {
        type: String,
        enum: ['by_location', 'by_type', 'seasonal']
    },
    tags: [{ type: String }],
    relatedDiseases: [{ type: String }],
    views: { type: Number, default: 0 },
    author: { type: String },
    reviewStatus: {
        type: String,
        enum: ['draft', 'reviewed', 'published'],
        default: 'draft'
    },
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
});

ArticleSchema.index({ tags: 1 });
ArticleSchema.index({ relatedDiseases: 1 });
ArticleSchema.index({ reviewStatus: 1, createdAt: -1 });

module.exports = mongoose.model('Article', ArticleSchema);
