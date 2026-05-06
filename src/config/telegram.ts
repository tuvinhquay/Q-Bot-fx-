import dotenv from "dotenv";

dotenv.config();

export const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN as string;

if (!TELEGRAM_TOKEN) {
  throw new Error("Thiếu TELEGRAM_BOT_TOKEN trong biến môi trường");
}
