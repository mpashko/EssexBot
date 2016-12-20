import requests
from bs4 import BeautifulSoup
import re

UAH = 'UAH'
USD = 'USD'
EUR = 'EUR'
RUB = 'RUB'


def get_currency(input):
    currencies = {USD: ['usd', 'дол'],
                  EUR: ['eur', 'евр'],
                  RUB: ['rub', 'руб'],
                  UAH: ['uah', 'грн', 'гри']}

    if isinstance(input, str):
        for key, value in currencies.items():
            if input[:3] in value:
                return key
    return False


class Currency:
    def __init__(self, title, ask, ask_delta, bid, bid_delta):
        self.title = title
        self.ask = ask
        self.ask_delta = ask_delta
        self.bid = bid
        self.bid_delta = bid_delta

    def __repr__(self):
        return self.title


class ExRateRequestor:
    def __init__(self):
        html = requests.get('http://minfin.com.ua/currency/').text
        self.parsed_html = BeautifulSoup(html, 'lxml')
        self.exrates = {}

    def formatting_delta_value(self, item):
        if float(item) > 0:
            return '+' + item
        elif float(item) == 0:
            return ' ' + item
        else:
            return item

    def get_exrates(self):
        if len(self.exrates) == 0:
            table = self.parsed_html.find('table', class_='mfm-table')
            rows = table.find_all('tr')

            for row in rows[1:4]:
                cells = row.find_all('td')
                currency_title_cell = cells[0]
                currency_title = get_currency(currency_title_cell.text.lower().strip())
                exrate_cell = cells[1]
                exrate_values = re.findall('[\d]+[,][\d]{,3}', exrate_cell.text)
                ask_value = exrate_values[0].replace(',', '.')
                bid_value = exrate_values[1].replace(',', '.')
                delta_values = exrate_cell.find_all('span')
                ask_delta = self.formatting_delta_value(delta_values[1].text)
                bid_delta = self.formatting_delta_value(delta_values[2].text)
                self.exrates[currency_title] = Currency(currency_title, ask_value, ask_delta, bid_value, bid_delta)
            return self.exrates
        else:
            return self.exrates

    def show_exrates(self, currency=None):
        exrates_dict = self.get_exrates()

        if currency is not None:
            required_exrate = exrates_dict[currency]
            return 'Покупка: {} | {}\n' \
                   'Продажа: {} | {}'.format(required_exrate.ask, required_exrate.ask_delta,
                                             required_exrate.bid, required_exrate.bid_delta)
        else:
            exrates_string = ''
            for value in exrates_dict.values():
                exrates_string += '{}\n' \
                                  'Покупка: {} | {}\n' \
                                  'Продажа: {} | {}\n' \
                                  '\n'.format(value.title, value.ask, value.ask_delta, value.bid, value.bid_delta)
            return exrates_string

    def convert_amount(self, amount, from_currency, to_currency):
        if to_currency in UAH:
            from_currency_exrate = self.get_exrates()[from_currency]
            required_amount = float(amount.replace(',', '.'))
            return round(required_amount * float(from_currency_exrate.bid), 1)
        else:
            to_currency_exrate = self.get_exrates()[to_currency]
            required_amount = float(amount.replace(',', '.'))
            return round(required_amount / float(to_currency_exrate.ask), 1)


if __name__ == "__main__":
    e = ExRateRequestor()
    print(e.convert_amount('200', 'Доллар (USD)', 'Гривна (UAH)'))
    print(e.convert_amount('12000', 'Гривна (UAH)', 'Евро (EUR)'))
