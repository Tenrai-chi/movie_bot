""" Логика взаимодействия с api OMDb """
import asyncio
import time
from configparser import ConfigParser
from typing import Union

import aiohttp
import mparser

config = ConfigParser()
config.read('config.ini')
API_TOKEN = config['ombd']['api_key']

url = 'http://www.omdbapi.com/'


async def search_movie_data(movie_title: str, year: Union[str, None] = 'empty') -> dict:  # в 3.9 нет |
    """ Запрос к api для получения информации о фильме """

    params = {
        't': movie_title,  # i по айди фильма
        'apikey': API_TOKEN,
        'plot': 'full',
        'type': 'movie',
        'y': year
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['Response'] == 'True':
                    answer = {
                        'data': convert_to_txt(data),
                        'imdbID': data['imdbID'],
                        'response': True,
                        'error': None,
                        'poster': data['Poster']
                    }
                    return answer
                else:
                    return {'error': 'Фильм не найден',
                            'response': False
                            }
            else:  # Почему-то всегда возвращает 200, даже если фильма нет, обрабатываю на response
                return {'error': 'Movie not found or API error',
                        'response': False}


def convert_to_txt(data: dict) -> str:
    """ Форматирование в текстовый вид """

    imd = 'N/A'
    rotten_tomatos = 'N/A'
    metacritic = 'N/A'
    try:
        imd = data['Ratings'][0]['Value']
        rotten_tomatos = data['Ratings'][1]['Value']
        metacritic = data['Ratings'][2]['Value']
    except IndexError as _:
        pass

    text = (
        f'Название: {data.get("Title", "N/A")}\n'
        f'Описание: {data.get("Plot", "N/A")}\n'  
        f'Тип: {data.get("Type", "N/A")}\n'
        f'Возрастной рейтинг: {data.get("Rated", "N/A")}\n'
        f'Релиз: {data.get("Released", "N/A")}\n'
        f'Длительность: {data.get("Runtime", "N/A")}\n'
        f'Жанр: {data.get("Genre", "N/A")}\n'
        f'Режиссер: {data.get("Director", "N/A")}\n'
        f'Сценарий: {data.get("Writer", "N/A")}\n'
        f'Актеры: {data.get("Actors", "N/A")}\n'
        f'Страна: {data.get("Country", "N/A")}\n'
        f'Награды: {data.get("Awards", "N/A")}\n'
        f'Сборы: {data.get("BoxOffice", "N/A")}\n'
        f'Постер: {data.get("Poster", "N/A")}\n'
        f'Рейтинг:\n'
        f'  IMD: {imd}\n'
        f'  Rotten Tomatoes: {rotten_tomatos}\n'
        f'  Metacritic: {metacritic}\n'
    )

    return text


async def get_random_film():
    """ Выдает информацию о случайном фильме """

    while True:  # Цикл для повторных попыток
        title = mparser.parse_movie_info()  # Получаем случайное название фильма
        info = await search_movie_data(title)  # Ищем информацию о фильме
        poster = info.get('poster', None)
        if poster is None:
            print('Повторяю попытку, нет постера')
            await asyncio.sleep(1)  # Используем await для асинхронного ожидания
            continue  # Если произошла ошибка, повторяем попытку

        if info['error'] is not None:
            print('Повторяю попытку, фильм не найден')
            await asyncio.sleep(1)
            continue

        return info
