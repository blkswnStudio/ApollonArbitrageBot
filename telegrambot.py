from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application, MessageHandler, filters
import requests
from buttons import Buttons

class ApollonTelegramBot:

    def __init__(self, token: str, chat_id: int) -> None:
        self.environment = ""
        # Variables
        self.token = token
        self.chat_id = chat_id
        # Telegram Bot
        self.app = Application.builder().token(token).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT, self.handler))

    def run(self):
        self.app.run_polling(0.5)

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.text == Buttons.get_oracle_info_name:

            await update.message.reply_text(f"Hallo BLKSWN-Family",
                                            reply_markup=Buttons.basic_markup)
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"👋 Hello, bot started ",
                                        reply_markup=Buttons.basic_markup)

    def get_zchf_price(self, network) -> float:
        response = requests.get(f'http://{self.tracking_api_host}:{self.tracking_api_port}'
                                f'/uniswap/prices/{network}/zchf_usdt/last').json()
        return float(round(response, 4))

    def send_telegram_msg(self, msg: str) -> None:
        telegram_msg = f"{msg}"
        response = requests.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            data={'chat_id': self.chat_id, 'text': telegram_msg}
        ).json()
        return response

    def send_telegram_msg_to_chat_id(self, msg: str, chat_id: str) -> None:
        telegram_msg = f"{msg}"
        response = requests.post(
            url=f'https://api.telegram.org/bot{self.token}/sendMessage',
            data={'chat_id': chat_id, 'text': telegram_msg}
        ).json()
        return response

