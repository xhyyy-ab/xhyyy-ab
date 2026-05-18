const mongoose = require('mongoose');

beforeAll(async () => {
    const url = process.env.MONGODB_URI || 'mongodb://localhost:27017/skincheck_test';
    await mongoose.connect(url);
});

afterAll(async () => {
    await mongoose.connection.close();
});

afterEach(async () => {
    const collections = mongoose.connection.collections;
    for (const key in collections) {
        await collections[key].deleteMany({});
    }
});
