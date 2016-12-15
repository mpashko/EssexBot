import requests
from bs4 import BeautifulSoup


class WeatherRequestor:
    def __init__(self):
        html = requests.get('https://sinoptik.ua/').text
        self.parsed_html = BeautifulSoup(html, 'lxml')

    def current_weather(self):
        current_temp = self.parsed_html.find('p', class_='today-temp').text
        description = self.parsed_html.find('div', class_='description').text.strip()
        weather_conditions = str(description) + ' Температура {}.'.format(current_temp)
        return weather_conditions


if __name__ == "__main__":
    weather_status = WeatherRequestor()
    print(weather_status.current_weather())
