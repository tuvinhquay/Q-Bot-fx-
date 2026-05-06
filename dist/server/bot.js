"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupBotHandlers = exports.bot = void 0;
const node_telegram_bot_api_1 = __importDefault(require("node-telegram-bot-api"));
const telegram_1 = require("../config/telegram");
exports.bot = new node_telegram_bot_api_1.default(telegram_1.TELEGRAM_TOKEN);
const setupBotHandlers = () => {
    exports.bot.onText(/\/start/, async (msg) => {
        const chatId = msg.chat.id;
        await exports.bot.sendMessage(chatId, `🤖 Q-Bot FX đã online!

Tôi là trợ lý giao dịch Forex của bạn.

Các lệnh bạn có thể dùng:
/help  - Danh sách lệnh
/status - Kiểm tra trạng thái bot
/signal - Lấy tín hiệu giao dịch mới nhất`);
    });
    exports.bot.onText(/\/help/, async (msg) => {
        const chatId = msg.chat.id;
        await exports.bot.sendMessage(chatId, `📖 HƯỚNG DẪN SỬ DỤNG Q-Bot FX

/status  → Kiểm tra server và MT5
/signal  → Lấy tín hiệu giao dịch mới nhất
/help    → Xem lại hướng dẫn`);
    });
    exports.bot.onText(/\/status/, async (msg) => {
        const chatId = msg.chat.id;
        await exports.bot.sendMessage(chatId, `🟢 Server đang hoạt động
⏳ Đang kết nối MT5...`);
    });
    exports.bot.onText(/\/signal/, async (msg) => {
        const chatId = msg.chat.id;
        await exports.bot.sendMessage(chatId, `📊 Đang phân tích thị trường...
Vui lòng chờ vài giây ⏳`);
    });
};
exports.setupBotHandlers = setupBotHandlers;
