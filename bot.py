# -*- coding: utf-8 -*-
import os
import re
import configparser
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,\
    CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from modules import exchange_rate


class Configurator:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.bot_name, self.token = self._define_bot_credentials()

    def _define_bot_credentials(self):
        bot_name = self.config["Active bot"]["bot"]
        if bot_name == "Essex":
            token = self.config[bot_name]["token"]
            return bot_name, token
        elif bot_name == "Irvine":
            token = self.config[bot_name]["token"]
            return bot_name, token


class TelegramBot:
    HELP_MESSAGE = "<b>Актуальные курсы валют и конвертер</b>\n" \
                   "- Получить средний курс валют в банках:\n" \
                   "  <i>курс [валюта] или [валюта]</i>\n" \
                   "- Перевод из любой валюты в гривны и обратно:\n" \
                   "  <i>[сумма] [валюта]\n" \
                   "  [сумма] гривен в [валюта]</i>\n" \
                   "Источник: www.minfin.com.ua/currency/\n"

    def __init__(self):
        config = Configurator()
        self.bot_name = config.bot_name
        self.token = config.token
        self.xrate_handler = exchange_rate.XrateHandler()
        self.updater = Updater(self.token)
        self.dp = self.updater.dispatcher
        self.define_operating_mode()

        self.dp.add_handler(CommandHandler("start", self.get_start_message))
        self.dp.add_handler(CommandHandler("help", self.get_help_message))
        self.dp.add_handler(MessageHandler(Filters.text, self.handling_message))
        self.dp.add_handler(CallbackQueryHandler(self.button))

        self.updater.idle()

    def define_operating_mode(self):
        if self.bot_name == "Essex":
            return self.webhook_mode()
        elif self.bot_name == "Irvine":
            return self.polling_mode()

    def webhook_mode(self):
        print("(!) Webhook mode")
        port = int(os.environ.get("PORT", 5000))
        self.updater.start_webhook(listen="0.0.0.0", port=port, url_path=self.token)
        self.updater.bot.setWebhook("https://essexbot.herokuapp.com/{}".format(self.token))

    def polling_mode(self):
        print("(!) Polling mode")
        return self.updater.start_polling()

    def get_start_message(self, bot, updater):
        updater.message.reply_text(
            text="Приветствую {}! Чем могу быть полезен?\n"
                 "\n{}\n"
                 "Если захочешь увидеть это сообщение еще раз - просто введи /help."
            .format(updater.message.from_user.first_name, self.HELP_MESSAGE),
            parse_mode="HTML",
            disable_web_page_preview=True)

    def get_help_message(self, bot, updater):
        updater.message.reply_text(text=self.HELP_MESSAGE,
                                   parse_mode="HTML",
                                   disable_web_page_preview=True)

    def handling_message(self, bot, updater):
        user_message = updater.message.text
        if "курс валют" in user_message:
            keyboard = [[InlineKeyboardButton("Доллар", callback_data="usd"),
                         InlineKeyboardButton("Евро", callback_data="eur"),
                         InlineKeyboardButton("Рубль", callback_data="rub")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            return updater.message.reply_text(text="Какая валюта интересует:",
                                              reply_markup=reply_markup)

        user_message_list = user_message.split(" ")
        for index in range(len(user_message_list)):
            currency = self._define_currency(user_message_list[index])
            amount = re.match("\d+[,.]?\d?", user_message_list[index])
            currency_to = None
            if amount:
                currency = self._define_currency(user_message_list[index + 1])

            if len(user_message_list) >= 3:
                try:
                    currency_to = self._define_currency(user_message_list[index + 3])
                except IndexError:
                    currency_to = self._define_currency(user_message_list[index + 2])

            if amount and currency and currency_to:
                amount = float(user_message_list[index].replace(",", "."))
                converted_amount = self.xrate_handler.convert_amount(amount, currency, currency_to)
                return updater.message.reply_text(text=converted_amount,
                                                  parse_mode="HTML",
                                                  disable_web_page_preview=True)

            elif amount and currency:
                amount = float(user_message_list[index].replace(",", "."))
                converted_amount = self.xrate_handler.convert_amount(amount, currency)
                return updater.message.reply_text(text=converted_amount,
                                                  parse_mode="HTML",
                                                  disable_web_page_preview=True)
            elif currency:
                xrate = self.xrate_handler.get_xrate_value(currency)
                return updater.message.reply_text(text=xrate,
                                                  parse_mode="HTML",
                                                  disable_web_page_preview=True)

    @staticmethod
    def _define_currency(word):
        prefix = word[:3].lower()
        if prefix in ["usd", "дол"]:
            return "usd"
        elif prefix in ["eur", "евр", "євр"]:
            return "eur"
        elif prefix in ["rub", "руб"]:
            return "rub"
        elif prefix in ["uah", "грн", "гри"]:
            return "uah"

    def button(self, bot, update):
        query = update.callback_query
        xrate_value = self.xrate_handler.get_xrate_value(query.data)
        bot.editMessageText(parse_mode="HTML",
                            disable_web_page_preview=True,
                            text=xrate_value,
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)

if __name__ == "__main__":
    bot = TelegramBot()
