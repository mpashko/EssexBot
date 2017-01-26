import requests
from bs4 import BeautifulSoup


class VacanciesRequestor:
    def __init__(self):
        html = requests.get('https://jobs.dou.ua/vacancies/?city=Киев&category=Python').text
        self.parsed_html = BeautifulSoup(html, 'lxml')



if __name__ == '__main__':
    v = VacanciesRequestor()
    print(v.html)