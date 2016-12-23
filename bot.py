# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from modules.weather import WeatherRequestor
from modules.exrates import *
from modules.movies import MoviesRequestor
import logging
import os

TOKEN = '286587089:AAEKSCnEp13jwzAc3TDH6Kv0114iCPCEAGI'     # EssexBot
#TOKEN = '312742066:AAEGHOcMgE4S3I-t--9GBiocKmjZWC84hBk'     # IrvineBot
PORT = int(os.environ.get("PORT", 5000))
HELP_MESSAGE = '<b>Актуальные курсы валют и конвертер</b>\n' \
               '- Получить средний курс валют в банках:\n' \
               '  <i>курс [валюта]</i>\n' \
               '- Перевод из любой валюты в гривны и обратно:\n' \
               '  <i>[сумма] [валюта] в гривне\n' \
               '  [сумма] гривен в [валюта]</i>\n'
EXRATE_MODULE = None

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_start_message(bot, updater):
    updater.message.reply_text(text='Приветствую {}! Чем могу быть полезен?\n'
                               '\n{}\n'
                               'Если захочешь увидеть это сообщение еще раз - просто введи /help.'
                               .format(updater.message.from_user.first_name, HELP_MESSAGE),
                               parse_mode='HTML')


def get_help_message(bot, updater):
    updater.message.reply_text(text=HELP_MESSAGE,
                               parse_mode='HTML')


def check_module():
    global EXRATE_MODULE
    if EXRATE_MODULE is None:
        EXRATE_MODULE = BanksExratesRequestor()
        return EXRATE_MODULE
    else:
        return EXRATE_MODULE


def check_message(bot, updater):
    user_message = updater.message.text.lower().split(' ')
    print(user_message)

    for i in range(len(user_message)):

        # Weather
        if "погода" in user_message[i]:
            updater.message.reply_text(WeatherRequestor().current_weather())

        # Exchange Rates
        if 'курс' in user_message[i] and 'валют' in user_message[i + 1]:
            keyboard = [[InlineKeyboardButton('Доллар', callback_data='usd'),
                         InlineKeyboardButton('Евро', callback_data='eur'),
                         InlineKeyboardButton('Рубль', callback_data='rub')]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            updater.message.reply_text(text='Какая валюта интересует:',
                                       reply_markup=reply_markup)

        if 'курс' in user_message[i] and get_currency(user_message[i + 1]):
            exrate = check_module()
            currency = get_currency(user_message[i + 1])
            exrate_value = exrate.get_exrate(currency=currency)

            updater.message.reply_text(text=exrate_value,
                                       parse_mode='HTML',
                                       disable_web_page_preview=True)

        if user_message[i].isdigit() and get_currency(user_message[i + 1]):
            amount = float(user_message[i].replace(',', '.'))
            from_currency = get_currency(user_message[i + 1])
            to_currency = get_currency(user_message[i + 3])

            if from_currency and to_currency and (from_currency is 'uah' or to_currency is 'uah'):
                exrate = check_module()
                converted_amount = exrate.convert_amount(amount, from_currency, to_currency)
                updater.message.reply_text(text='{} {} = {} {}'
                                           .format(amount, from_currency.upper(),
                                                   converted_amount, to_currency.upper()))
            else:
                updater.message.reply_text('К сожалению, могу проводить конвертацию только в / из гривны.')

        # Movies
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


def button(bot, update):
    query = update.callback_query
    exrate = check_module()
    exrate_value = exrate.get_exrate(currency=query.data)
    bot.editMessageText(parse_mode='HTML',
                        disable_web_page_preview=True,
                        text=exrate_value,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)


def main():
    updater = Updater(TOKEN)

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.setWebhook("https://essexbot.herokuapp.com/" + TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', get_start_message))
    dp.add_handler(CommandHandler('help', get_help_message))
    dp.add_handler(MessageHandler(Filters.text, check_message))
    dp.add_handler(CallbackQueryHandler(button))

    #updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
