const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const FavoriteSchema = new Schema({
    id: { type: String, required: true, unique: true },
    userId: { type: String, required: true, index: true },
    articleId: { type: String, required: true },
    createdAt: { type: Date, default: Date.now }
});

FavoriteSchema.index({ userId: 1, articleId: 1 }, { unique: true });

module.exports = mongoose.model('Favorite', FavoriteSchema);
