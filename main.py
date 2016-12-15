# -*- coding: utf-8 -*-
#
# EssexBot

import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from modules.exrate import ExRateRequestor
from modules.weather import WeatherRequestor

TOKEN = "286587089:AAEKSCnEp13jwzAc3TDH6Kv0114iCPCEAGI"
PORT = int(os.environ.get("PORT", "5000"))

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def get_start_message(bot, update):
    update.message.reply_text("Приветствую {}! Чем могу быть полезен?\n"
                              "\n"
                              "На данный момент, могу подсказать прогноз погоды на сегодня в Киеве,"
                              " а также актуальный курс валют.\n"
                              "\n"
                              "Если хочешь увидеть это сообщение еще раз - просто введи /help."
                              .format(update.message.from_user.first_name))


def get_help_message(bot, update):
    update.message.reply_text("На данный момент, могу подсказать прогноз погоды на сегодня в Киеве,"
                              " а также актуальный курс валют.\n")


def check_message(bot, updater):
    if "погода" in updater.message.text.lower():
        actual_weather = WeatherRequestor()
        updater.message.reply_text(actual_weather.current_weather())

    if "курс валют" in updater.message.text.lower():
        actual_exrate = ExRateRequestor()
        updater.message.reply_text(actual_exrate.show_required_currency("USD"))


def main():
    # Main Updater with Webhook
    updater = Updater(TOKEN)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.setWebhook("https://essexbot.herokuapp.com/" + TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", get_start_message))
    dp.add_handler(CommandHandler("help", get_help_message))

    # on noncommand i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, check_message))

    # Comment out the line below before commit
    #updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
