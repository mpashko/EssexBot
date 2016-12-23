import requests
import datetime

TOKEN = 'b73aefb24253af83b2e8eb37f852e73125497748'
URL_BASE = 'http://api.minfin.com.ua/'


def get_currency(user_input):
    currencies = {'usd': ['usd', 'дол'],
                  'eur': ['eur', 'евр'],
                  'rub': ['rub', 'руб'],
                  'uah': ['uah', 'грн', 'гри']}

    if isinstance(user_input, str):
        for key, value in currencies.items():
            if user_input[:3] in value:
                return key
    return False


class BanksExratesRequestor:
    def __init__(self):
        self.url = URL_BASE + 'summary/' + TOKEN + '/'
        self.response = None

    def get_response(self):
        exrate_json = requests.get(self.url).json()

        # exrate_json = {'usd': {'bid': '26.4000', 'trendAsk': -0.099999999999998, 'ask': '27.1000', 'trendBid': 0},
        #                'rub': {'bid': '0.4000', 'trendAsk': 0, 'ask': '0.4400', 'trendBid': 0},
        #                'eur': {'bid': '27.4000', 'trendAsk': -0.029999999999998, 'ask': '28.3350', 'trendBid': 0},
        #                'gbp': {'bid': '32.0000', 'trendAsk': -0.2, 'ask': '33.3000', 'trendBid': 0}}

        last_update = datetime.datetime.now()
        self.response = [exrate_json, last_update]
        #print(exrate_json)
        print('(!) Exrates have been updated at', last_update)

    def check_last_response(self):
        current_time = datetime.datetime.now()
        if self.response is None:
            return True
        elif current_time >= self.response[1] + datetime.timedelta(minutes=10):
            return True
        else:
            return False

    def update_exrate(self):
        if self.check_last_response():
            self.get_response()

    def add_trend_arrow(self, exrate_trend):
        if exrate_trend < 0:
            return '(▼'
        elif exrate_trend > 0:
            return '(▲'
        else:
            return ''

    def get_exrate(self, currency):
        self.update_exrate()
        exrate = self.response[0][currency]
        bid = exrate['bid'][:-1]
        ask = exrate['ask'][:-1]
        trendBid = exrate['trendBid']
        trendAsk = exrate['trendAsk']
        arrow_trendBid = self.add_trend_arrow(trendBid)
        arrow_trendAsk = self.add_trend_arrow(trendAsk)
        trendBid = str(trendBid)[:5] + ')' if trendBid != 0 else ''
        trendAsk = str(trendAsk)[:5] + ')' if trendAsk != 0 else ''

        return '<b>Актуальный курс {}</b>\n' \
               'Покупка: {} {} {}\n' \
               'Продажа: {} {} {}\n' \
               'Источник: www.minfin.com.ua/currency/'.format(currency.upper(),
                                                              bid, arrow_trendBid, trendBid,
                                                              ask, arrow_trendAsk, trendAsk)

    def convert_amount(self, amount, from_currency, to_currency):
        self.update_exrate()

        if to_currency in 'uah':
            from_currency_exrate = self.response[0][from_currency]['ask']
            return round(amount * float(from_currency_exrate), 1)
        else:
            to_currency_exrate = self.response[0][to_currency]['bid']
            return round(amount / float(to_currency_exrate), 1)


if __name__ == '__main__':
    e = BanksExratesRequestor()
    # while True:
    #     a = input('currency? ')
    #     a_upd = get_currency(a)
    #     print(e.get_exrate(a_upd))
    print(e.convert_amount(120, 'usd', 'uah'))
    print(e.convert_amount(6.54, 'uah', 'eur'))