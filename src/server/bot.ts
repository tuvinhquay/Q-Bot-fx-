import TelegramBot from "node-telegram-bot-api";
import { TELEGRAM_TOKEN } from "../config/telegram";

export const bot = new TelegramBot(TELEGRAM_TOKEN);

export const setupBotHandlers = () => {
  bot.onText(/\/start/, async (msg) => {
    const chatId = msg.chat.id;

    await bot.sendMessage(
      chatId,
      `🤖 Q-Bot FX đã online!

Tôi là trợ lý giao dịch Forex của bạn.

Các lệnh bạn có thể dùng:
/help  - Danh sách lệnh
/status - Kiểm tra trạng thái bot
/signal - Lấy tín hiệu giao dịch mới nhất`
    );
  });

  bot.onText(/\/help/, async (msg) => {
    const chatId = msg.chat.id;

    await bot.sendMessage(
      chatId,
      `📖 HƯỚNG DẪN SỬ DỤNG Q-Bot FX

/status  → Kiểm tra server và MT5
/signal  → Lấy tín hiệu giao dịch mới nhất
/help    → Xem lại hướng dẫn`
    );
  });

  bot.onText(/\/status/, async (msg) => {
    const chatId = msg.chat.id;

    await bot.sendMessage(
      chatId,
      `🟢 Server đang hoạt động
⏳ Đang kết nối MT5...`
    );
  });

  bot.onText(/\/signal/, async (msg) => {
    const chatId = msg.chat.id;

    await bot.sendMessage(
      chatId,
      `📊 Đang phân tích thị trường...
Vui lòng chờ vài giây ⏳`
    );
  });
};
