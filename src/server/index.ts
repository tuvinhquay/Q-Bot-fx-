import express from "express";
import bodyParser from "body-parser";
import { bot, setupBotHandlers } from "./bot";

const app = express();
app.use(bodyParser.json());

setupBotHandlers();

app.post("/webhook", (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

app.get("/", (_, res) => {
  res.json({ status: "Q-Bot FX Telegram Server is running" });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log("Server running on port " + PORT);
});
