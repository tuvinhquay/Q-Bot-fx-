require("dotenv").config({ path: require("path").join(__dirname, "../.env") });

const http = require("http");
const { bot, botStatus } = require("./telegramBot");

const port = process.env.PORT || 3000;

function sendJson(res, statusCode, payload) {
  res.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(payload));
}

function buildTelegramHealthPayload() {
  const telegramReady = Boolean(bot && botStatus.running);

  return {
    status: telegramReady ? "ok" : "degraded",
    component: "telegram_bot",
    time: new Date().toISOString(),
    telegram: {
      configured: botStatus.configured,
      running: botStatus.running,
      lastError: botStatus.lastError,
    },
  };
}

const server = http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    const payload = buildTelegramHealthPayload();
    sendJson(res, payload.status === "ok" ? 200 : 503, payload);
    return;
  }

  if (req.method === "GET" && req.url === "/api/health") {
    sendJson(res, 200, {
      status: "ok",
      component: "backend_api",
      time: new Date().toISOString(),
    });
    return;
  }

  sendJson(res, 404, {
    status: "not_found",
    time: new Date().toISOString(),
  });
});

server.listen(port, () => {
  console.log(`🩺 Health API đang chạy tại http://localhost:${port}`);
});
