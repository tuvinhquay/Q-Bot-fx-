const TelegramBot = require("node-telegram-bot-api");

const token = process.env.TELEGRAM_BOT_TOKEN;

const botStatus = {
  configured: Boolean(token),
  running: false,
  lastError: null,
};

let bot = null;

if (!token) {
  botStatus.lastError = "Thiếu TELEGRAM_BOT_TOKEN";
  console.error("❌ Thiếu TELEGRAM_BOT_TOKEN. Bot Telegram không được khởi động.");
} else {
  bot = new TelegramBot(token, { polling: true });
  botStatus.running = true;

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
    botStatus.running = false;
    botStatus.lastError = error.message;
    console.error("Polling error:", error);
  });
}

module.exports = { bot, botStatus };
