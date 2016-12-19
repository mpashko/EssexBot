import requests
from bs4 import BeautifulSoup
import re


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

    def get_currency(self, input):
        currencies = {'USD': ['usd', 'дол'],
                      'EUR': ['eur', 'евр'],
                      'RUB': ['rub', 'руб'],
                      'UAH': ['uah', 'грн', 'гри']}

        if isinstance(input, str):
            for key, value in currencies.items():
                if input[:3] in value:
                    return key
        return False

    def formating_delta_value(self, item):
        if float(item) > 0:
            return '+' + item
        elif float(item) == 0:
            return ' ' + item
        else:
            return item

    def get_exrates(self):
        table = self.parsed_html.find('table', class_='mfm-table')
        rows = table.find_all('tr')

        header = rows[0]
        cash_market_cell = header.find_all('th')[1]
        cash_market_header = cash_market_cell.find('small').text.split('/')
        ask_header = cash_market_header[0].strip()
        bid_header = cash_market_header[1].strip()

        exrates = []
        for row in rows[1:4]:
            cells = row.find_all('td')
            currency_title_cell = cells[0]
            currency_title = self.get_currency(currency_title_cell.text.lower().strip())
            exrate_cell = cells[1]
            exrate_values = re.findall('[\d]+[,][\d]{,3}', exrate_cell.text)
            ask_value = exrate_values[0]
            bid_value = exrate_values[1]
            delta_values = exrate_cell.find_all('span')
            ask_delta = self.formating_delta_value(delta_values[1].text)
            bid_delta = self.formating_delta_value(delta_values[2].text)
            exrates.append(Currency(currency_title, ask_value, ask_delta, bid_value, bid_delta))
        return exrates

    def get_details(self, currency=None):
        exrates_list = self.get_exrates()
        exrates_string = ''
        for exrate in exrates_list:
            if exrate.title is currency:
                return '{}\n' \
                       'Покупка: {} | {}\n' \
                       'Продажа: {} | {}'.format(exrate.title, exrate.ask, exrate.ask_delta,
                                                 exrate.bid, exrate.bid_delta)
            else:
                exrates_string += '{}\n' \
                                  'Покупка: {} | {}\n' \
                                  'Продажа: {} | {}\n' \
                                  '\n'.format(exrate.title, exrate.ask, exrate.ask_delta,
                                              exrate.bid, exrate.bid_delta)
        return exrates_string

    # def show_all_exrates(self):
    #
    #     for curreny in exrate_status


    #     purchase_header = rows[0].find_all('td')[1].text
    #     sale_header = rows[0].find_all('td')[2].text
    #     #nbu_header = rows[0].find_all('td')[3].text

        # for row in rows[1:]:
        #     print(row)
    #         currency = row.find('th').text
    #         purchase_value = row.find_all('td')[0].text
    #         sale_value = row.find_all('td')[1].text
    #         #nbu_value = row.find_all('td')[2].text
    #
    #         purchase_exrate = self.find_exrate_in_string(purchase_value)
    #         sale_exrate = self.find_exrate_in_string(sale_value)
    #         #nbu_exrate = self.find_exrate_in_string(nbu_value)
    #
    #         exrate_dict[currency] = {purchase_header: purchase_exrate, sale_header: sale_exrate}
    #                                         #nbu_header: nbu_exrate}
    #     return exrate_dict
    #
    # def find_exrate_in_string(self, string):
    #     exrate_in_string = re.match('[\d]+[.][\d]{,4}', string).group(0)
    #     exrate_float = float(exrate_in_string)
    #     return exrate_float
    #
    #
    # def to_string(self, exrate_dict, currency=None):
    #     exrate_string = ""
    #     flag = False if False in [type(value) is dict for value in exrate_dict.values()] else True
    #     if flag is True:
    #         for key, value in exrate_dict.items():
    #             exrate_string += "{}\n".format(key)
    #             for header, exrate in value.items():
    #                 exrate_string += "{}: {}\n".format(header, exrate)
    #             exrate_string += "\n"
    #     else:
    #         exrate_string += "{}\n".format(currency)
    #         for header, exrate in exrate_dict.items():
    #             exrate_string += "{}: {}\n".format(header, exrate)
    #         exrate_string += "\n"
    #     return exrate_string
    #
    # def show_required_currency(self, currency=None):
    #     required_currency_exrate = self.get_exrate_dict()[currency] if currency is not None else self.get_exrate_dict()
    #     return self.to_string(required_currency_exrate, currency=currency)
    #
    # def convert_amount(self, amount, from_currency, to_currency):
    #     if to_currency is "UAH":
    #         from_currency_exrate = self.get_exrate_dict()[from_currency]
    #         return round(amount * from_currency_exrate["Покупка"], 1)
    #     else:
    #         from_currency_exrate = self.get_exrate_dict()[to_currency]
    #         return round(amount / from_currency_exrate["Продажа"], 1)





if __name__ == "__main__":
    exrate_status = ExRateRequestor()
    print(exrate_status.get_details())
    #exrate_status.get_exrates()
    # print(exrate_status.show_required_currency())
    # print(exrate_status.show_required_currency("RUB"))
    # print(exrate_status.convert_amount(200, "USD", "UAH"))
