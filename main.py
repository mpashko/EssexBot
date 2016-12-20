# -*- coding: utf-8 -*-
import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from modules.exrates import *
from modules.weather import WeatherRequestor
from modules.movies import MoviesRequestor

TOKEN = "286587089:AAEKSCnEp13jwzAc3TDH6Kv0114iCPCEAGI"    # EssexBot
#TOKEN = "299609446:AAGk2Gwyr3s-OV_AGBXGVj6wKudVoG_yQoE"     # AdiutorBot
PORT = int(os.environ.get("PORT", 5000))

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def get_start_message(bot, updater):
    updater.message.reply_text("Приветствую {}! Чем могу быть полезен?\n"
                               "\n"
                               "На данный момент, могу помочь со следующим:\n"
                               "- Подсказать прогноз [погоды] в Киеве на сегодня;\n"
                               "- Посоветовать новый [фильм] к просмотру;\n"
                               "- Показать рейтинг N популярных фильмов на данный момент;\n"
                               "- Показать актуальный [курс] [валют];\n"
                               "- Конвертировать валюты в гривну, и из гривны.\n"
                               "\n"
                               "Если хочешь увидеть это сообщение еще раз - просто введи /help."
                               .format(updater.message.from_user.first_name))


def get_help_message(bot, updater):
    updater.message.reply_text("На данный момент, могу подсказать прогноз погоды на сегодня в Киеве,"
                               " а также актуальный курс валют.\n")


def check_message(bot, updater):
    user_message = updater.message.text.lower().split(" ")
    print(user_message)

    for i in range(len(user_message)):


        # WEATHER
        if "погода" in user_message[i]:
            updater.message.reply_text(WeatherRequestor().current_weather())


        # MOVIES
        if user_message[i][:4] in ["филь", "кино"]:
            if user_message[i - 1].isdigit():
                quantity = int(user_message[i - 1])
                top_movies = MoviesRequestor().get_actual_movie_list(limit=quantity)
                updater.message.reply_text(parse_mode="HTML",
                                           disable_web_page_preview=True,
                                           text="Лучшие {} фильмов на данный момент:\n{}".format(quantity, top_movies))
            else:
                movies = MoviesRequestor().get_actual_movie_list()
                updater.message.reply_text(parse_mode="HTML",
                                           disable_web_page_preview=False,
                                           text="Советую посмотреть {}".format(movies))


        # EXCHANGE RATE
        if "валют" in user_message[i]:
            updater.message.reply_text(ExRateRequestor().show_exrates())

        if "курс" in user_message[i] and get_currency(user_message[i + 1]):    # Could be fixed - call 1 func 2 times
            currency = get_currency(user_message[i + 1])
            currency_exrate = ExRateRequestor().show_exrates(currency=currency)
            updater.message.reply_text("Актуальный курс на сейчас:\n{}".format(currency_exrate))

        if user_message[i].isdigit() and get_currency(user_message[i + 1]):
            amount = user_message[i]
            from_currency = get_currency(user_message[i + 1])
            to_currency = get_currency(user_message[i + 3])

            if from_currency and to_currency and (from_currency is UAH or to_currency is UAH):
                converted_amount = ExRateRequestor().convert_amount(amount, from_currency, to_currency)
                updater.message.reply_text("{} {}".format(converted_amount, to_currency))
            else:
                updater.message.reply_text("К сожалению, на данный момент, могу проводить конвертацию только"
                                           " с гривнами.")


        # OTHER
        if user_message[i] in ["привет", "здравствуй"]:
            updater.message.reply_text("Приветствую {}!".format(updater.message.from_user.first_name))


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
