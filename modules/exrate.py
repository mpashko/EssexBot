import requests
from bs4 import BeautifulSoup
import re


class ExRateRequestor:
    def __init__(self):
        html = requests.get('http://finance.i.ua/').text
        self.parsed_html = BeautifulSoup(html, 'lxml')

    def find_exrate_in_string(self, string):
        exrate_in_string = re.match('[\d]+[.][\d]{,4}', string).group(0)
        exrate_float = float(exrate_in_string)
        return exrate_float

    def get_exrate_dict(self):
        table = self.parsed_html.find('table', class_='table table-data -important')
        rows = table.find_all('tr')
        purchase_header = rows[0].find_all('td')[1].text
        sale_header = rows[0].find_all('td')[2].text
        nbu_header = rows[0].find_all('td')[3].text

        exrate_dict = {}
        for row in rows[1:]:
            currency = row.find('th').text
            purchase_value = row.find_all('td')[0].text
            sale_value = row.find_all('td')[1].text
            nbu_value = row.find_all('td')[2].text

            purchase_exrate = self.find_exrate_in_string(purchase_value)
            sale_exrate = self.find_exrate_in_string(sale_value)
            nbu_exrate = self.find_exrate_in_string(nbu_value)

            exrate_dict[currency] = {purchase_header: purchase_exrate, sale_header: sale_exrate,
                                            nbu_header: nbu_exrate}
        return exrate_dict

    def to_string(self, exrate_dict, currency=None):
        exrate_string = ""
        flag = False if False in [type(value) is dict for value in exrate_dict.values()] else True
        if flag is True:
            for key, value in exrate_dict.items():
                exrate_string += "{}\n".format(key)
                for header, exrate in value.items():
                    exrate_string += "{}: {}\n".format(header, exrate)
                exrate_string += "\n"
        else:
            exrate_string += "{}\n".format(currency)
            for header, exrate in exrate_dict.items():
                exrate_string += "{}: {}\n".format(header, exrate)
            exrate_string += "\n"
        return exrate_string

    def show_required_currency(self, currency):
        required_currency_exrate = self.get_exrate_dict()[currency]
        return self.to_string(required_currency_exrate, currency=currency)


if __name__ == "__main__":
    exrate_status = ExRateRequestor()
    print(exrate_status.show_required_currency("USD"))
