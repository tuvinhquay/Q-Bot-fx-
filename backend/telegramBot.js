require("dotenv").config();
const TelegramBot = require("node-telegram-bot-api");

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;

if (!token) {
  console.error("❌ Thiếu TELEGRAM_BOT_TOKEN");
  process.exit(1);
}

const bot = new TelegramBot(token, { polling: true });

console.log("🤖 Telegram Bot đang chạy...");

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id,
`🤖 Q-Bot-FX đã online!

Các lệnh:
📊 /status – Kiểm tra hệ thống
💰 /balance – Xem số dư
🚀 /ping – Kiểm tra kết nối`
  );
});

bot.onText(/\/ping/, (msg) => {
  bot.sendMessage(msg.chat.id, "🏓 Pong! Bot đang hoạt động.");
});

bot.onText(/\/status/, (msg) => {
  bot.sendMessage(msg.chat.id,
`📡 TRẠNG THÁI HỆ THỐNG

Server: 🟢 Online
Bot: 🟢 Running
Trading Engine: 🟡 Chưa bật`
  );
});

bot.onText(/\/balance/, (msg) => {
  bot.sendMessage(msg.chat.id,
`💰 SỐ DƯ HIỆN TẠI

USDT: 0
BTC: 0
PNL hôm nay: 0%`
  );
});

bot.on("polling_error", (error) => {
  console.error("Polling error:", error);
});
