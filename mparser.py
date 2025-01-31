import requests
from bs4 import BeautifulSoup


def parse_movie_info():
    """ Получить название случайного фильма из randomfilm """
    url = "https://randomfilm.ru/"
    response = requests.get(url)

    if response.status_code != 200:
        print("Не удалось получить страницу.")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    title_element = soup.find('h2')
    if title_element:
        title = title_element.text.strip()
        parts = title.split('/')
        if len(parts) > 1:
            return parts[1].strip()
        return title
    return
