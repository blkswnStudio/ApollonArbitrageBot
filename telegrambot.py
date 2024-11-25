from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application, MessageHandler, filters
import requests
import time
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

        self.data = None

    def run(self):
        self.app.run_polling(1.0)

    async def handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            print('Vorher')
            if update.message.text == Buttons.get_current_data_name:
                print('Nachher')
                message = "Time: " + f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}\n"
                message += "Asset, Oracle/Dex, Premium\n"
                for name in self.data:
                    message += f"{name}, {self.data[name]['dex_price']:.2f} jUSD / YF_Oracle: {self.data[name]['yf_price']:.2f} $, {self.data[name]['premium']:.2f} %\n"  #
                await update.message.reply_text(message,
                                                reply_markup=Buttons.basic_markup)
        except Exception as e:
            print(f"Error: {e}")
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"👋 Hello, bot started ",
                                        reply_markup=Buttons.basic_markup)

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

