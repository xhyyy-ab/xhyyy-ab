const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const UserSchema = new Schema({
    unionId: { type: String, required: true, unique: true },
    openId: { type: String, required: true },
    nickName: { type: String, default: '微信用户' },
    avatarUrl: { type: String, default: '' },
    createdAt: { type: Date, default: Date.now },
    lastLoginAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', UserSchema);
