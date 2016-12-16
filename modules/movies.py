import requests
from bs4 import BeautifulSoup
import re


def get_key(movie):
    return float(movie.rating)


class Movie:
    def __init__(self, name, countries, rating):
        self.name = name
        self.countries = countries
        self.rating = rating

    def __repr__(self):
        return self.name


class MoviesRequestor:
    def __init__(self):
        html = requests.get('https://kinoafisha.ua/kinoafisha/').text
        self.parsed_html_document = BeautifulSoup(html, 'lxml')

    def to_message(self, movie_list):
        message = ""
        for i in range(len(movie_list)):
            message += "{}. {} ({})\n".format(i + 1, movie_list[i].name, movie_list[i].rating)
        return message

    def get_actual_movie_list(self, limit=3):          # limit -1 список всех фильмов
        movie_list = []
        movies_divs = self.parsed_html_document.find_all('div', class_='text')
        movies_divs.pop()
        for movie_html in movies_divs:
            movie = BeautifulSoup(str(movie_html), 'lxml')

            name = movie.find('h3').text
            countries = movie.find('div', class_='countries').text.strip()
            rating = movie.find('div', class_='rating').text.strip()
            rating_value = re.match('[\d]+[.,][\d]+', rating).group(0).replace(',', '.')

            movie_list.append(Movie(name, countries, rating_value))
        sorted_movie_list = sorted(movie_list, key=get_key, reverse=True)
        return self.to_message(sorted_movie_list[:limit])


if __name__ == "__main__":
    movies = MoviesRequestor()
    print(movies.get_actual_movie_list(12))
