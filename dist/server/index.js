"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const body_parser_1 = __importDefault(require("body-parser"));
const bot_1 = require("./bot");
const app = (0, express_1.default)();
app.use(body_parser_1.default.json());
(0, bot_1.setupBotHandlers)();
app.post("/webhook", (req, res) => {
    bot_1.bot.processUpdate(req.body);
    res.sendStatus(200);
});
app.get("/", (_, res) => {
    res.json({ status: "Q-Bot FX Telegram Server is running" });
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log("Server running on port " + PORT);
});
