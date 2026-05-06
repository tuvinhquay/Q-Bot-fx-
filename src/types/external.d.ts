declare const process: {
  env: Record<string, string | undefined>;
};

declare module "dotenv" {
  const dotenv: {
    config: () => void;
  };

  export default dotenv;
}

declare module "express" {
  type Request = { body: unknown };
  type Response = {
    json: (body: unknown) => void;
    sendStatus: (statusCode: number) => void;
  };
  type Handler = (req: Request, res: Response) => void;
  type GetHandler = (req: Request, res: Response) => void;

  type ExpressApp = {
    use: (middleware: unknown) => void;
    post: (path: string, handler: Handler) => void;
    get: (path: string, handler: GetHandler) => void;
    listen: (port: string | number, callback: () => void) => void;
  };

  const express: () => ExpressApp;
  export default express;
}

declare module "body-parser" {
  const bodyParser: {
    json: () => unknown;
  };

  export default bodyParser;
}

declare module "node-telegram-bot-api" {
  type ChatId = string | number;
  type TelegramMessage = {
    chat: {
      id: ChatId;
    };
  };

  class TelegramBot {
    constructor(token: string);
    onText(
      regexp: RegExp,
      callback: (msg: TelegramMessage) => void | Promise<void>
    ): void;
    sendMessage(chatId: ChatId, text: string): Promise<unknown>;
    processUpdate(update: unknown): void;
  }

  export default TelegramBot;
}
