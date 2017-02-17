"""
Current module responsible for exchange rates requests and amount conversions
to different currencies.
"""
import requests
from datetime import datetime, timedelta


class CurrencyError(Exception):
    """
    Exception raised for incorrect currency title in the input.
    """
    def __str__(self):
        return "Incorrect currency title"


class Updater:
    """
    Responsible for requests and updates to actual exchange rates.
    """
    URL_BASE = "http://api.minfin.com.ua"
    TOKEN = "b73aefb24253af83b2e8eb37f852e73125497748"

    def __init__(self):
        self.url = "{}/summary/{}/".format(self.URL_BASE, self.TOKEN)
        self.response = None
        self.last_response_time = None

    def get_update(self):
        """
        Function checks that we have an actual data, otherwise request data
        from the server.
        """
        if self.last_response_time is None:
            self.get_response()
        present_time = datetime.now()
        if present_time >= self.last_response_time + timedelta(minutes=10):
            self.get_response()

    def get_response(self):
        """
        Function requests actual data from the server (in JSON format) and
        stores time of the last request.
        """
        self.response = requests.get(self.url).json()
        self.last_response_time = datetime.now()
        print("(!) Xrates have been updated at", self.last_response_time)


class XrateHandler:
    """
    Responsible for handling of available exchange rates data.
    Handles the following input data:
        [currency]
        [amount][currency] - converts amount to "uah"
        [amount][from_currency][to_currency]
    """
    def __init__(self):
        self.updater = Updater()

    def get_xrate_value(self, user_input):
        """
        Function returns the exchange rates values based on the user input.

        Args:
            user_input (str): Should be either "usd" or "eur" or "rub".

        Returns:
           str: "Курс [user_input]:
                 ← Покупка: [bid] [trend_bid]
                 → Продажа: [ask] [trend_ask]".

        Raises:
            CurrencyError: For incorrect currency title in the input.
        """
        self.updater.get_update()

        try:
            xrate_data = self.updater.response[user_input]
        except KeyError:
            raise CurrencyError

        bid = xrate_data["bid"][:-1]
        ask = xrate_data["ask"][:-1]
        trend_bid = xrate_data["trendBid"]
        trend_ask = xrate_data["trendAsk"]
        trend_bid_arrow = self._add_trend_arrow(trend_bid)
        trend_ask_arrow = self._add_trend_arrow(trend_ask)
        trend_bid_str = "({} {})".format(trend_bid_arrow, round(trend_bid, 3))\
            if trend_bid != 0.0 else ""
        trend_ask_str = "({} {})".format(trend_ask_arrow, round(trend_ask, 3))\
            if trend_ask != 0.0 else ""

        return "Курс {}:\n" \
               "← Покупка: {} {}\n" \
               "→ Продажа: {} {}\n"\
            .format(user_input,
                    bid, trend_bid_str,
                    ask, trend_ask_str)

    @staticmethod
    def _add_trend_arrow(xrate_trend):
        """
        Function adds trend arrow based on the trend value.

        Args:
            xrate_trend (float): Exchange rate trend value.

        Returns:
            str: "▼" if trend value is lower than zero.
                 "▲" if trend value is higher than zero.
        """
        if xrate_trend < 0:
            return "▼"
        elif xrate_trend > 0:
            return "▲"

    def convert_amount(self, amount, from_currency, to_currency="uah"):
        """
        Converts amount from required currency to another one.

        Args:
            amount (float).
            from_currency (str): Should be either "usd" or "eur" or "rub"
                or "uah". In case of "uah", [to_currency] should be specified,
                otherwise it could be left by default.
            to_currency (str, optional): Defaults to "uah", otherwise should be
                either "usd" or "eur" or "rub".

        Returns:
            str: Result of "_return_string" function.
        """
        self.updater.get_update()

        if to_currency in "uah":
            xrate = self.updater.response[from_currency]["ask"]
            converted_amount = round(amount * float(xrate), 2)
            return self._return_string(amount, from_currency,
                                       converted_amount, to_currency)
        else:
            xrate = self.updater.response[to_currency]["bid"]
            converted_amount = round(amount / float(xrate), 2)
            return self._return_string(amount, from_currency,
                                       converted_amount, to_currency)

    def _return_string(self, amount, from_currency, converted_amount,
                       to_currency):
        """
        Forms a string from the input data.

        Args:
            amount (int or float).
            from_currency (str).
            converted_amount (int or float).
            to_currency (str).

        Returns:
            str: "[amount] [from_currency] = [converted_amount] [to_currency]".
        """
        amount_str = self._convert_to_str(amount)
        converted_amount_str = self._convert_to_str(converted_amount)
        return "{} {} = {} {}".format(amount_str, from_currency,
                                      converted_amount_str, to_currency)

    @staticmethod
    def _convert_to_str(amount):
        """
        Converts amount to string type. Adds white spaces for better readings.

        Args:
            amount (int or float).

        Returns:
            str: [amount].

        Example:
            >>> print(XrateHandler._convert_to_str(10000))
            10 000
            >>> print(XrateHandler._convert_to_str(1000.10))
            1 000.1
            >>> print(XrateHandler._convert_to_str(100.01))
            100.01
        """
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount should be int or float type")

        amount_str = str(amount)
        amount_list = list(amount_str)[::-1]

        try:
            i = amount_list.index(".")
        except ValueError:
            i = -1

        while True:
            i += 4
            if i >= len(amount_list):
                break
            amount_list.insert(i, " ")

        return "".join(amount_list[::-1])
