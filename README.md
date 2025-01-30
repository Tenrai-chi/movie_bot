# movie_bot
Телеграм бот для получения информации о фильмах с помощью OMDb API
## Функционал
* Для доступа к боту пользователю необходимо ввести ключ с помощью команды /activate <ключ>, если пользователь попытается сделать запрос к боту не авторизовавшись, то бот уведомит его о необходимости авторизации
* С помощью бота можно получить информацию:
    - Название
    - Описание
    - Тип
    - Возрастной рейтинг
    - Релиз
    - Длительность
    - Жанр
    - Режисер
    - Автор сценария
    - Актеры
    - Страна выпуска
    - Полученные награды
    - Сборы
    - Постер
    - Рейтинг (IMD, Tomatoes, Metacritic)
* База данных Postgreql, взаимодействие с ней происходит через SqlAlchemy и pg8000
  Таблица user. Хранит данные о авторизированных пользователях:
  |  id  | user_telegram_id |  last_request  | username |
  |------|------------------|----------------|----------|
  | auto |        int       |     datetime   |    str   |
      
* Таблица request. Хранит данные успешных запросах:
  |  id  | user_id |  imdbID  | date_time |
  |------|---------|----------|-----------|
  | auto |   int   | char(50) |  datetime |
    
* Таблица bad_request. Хранит данные о неуспешных запросах и вызванных ошибках:
  |  id  | user_id |   title  | date_time |    error   |
  |------|---------|----------|-----------|------------|
  | auto |   int   | char(50) |  datetime |  char(200) |
  
* **Планируемые улучшения:**
    - [ ] Запуск с помощью Docker
    - [ ] Подписки base, medium, maximum, которая оозначает максимальное количество запросов в сутки. 5, 10 и 50 соответственно. Base дается автоматически всем авторизованным пользователям.
    - [ ] Покупка подписок с помощью бота через Telegram Payments
    - [ ] Запись транзакций при покупке подписок
    - [ ] Перевод полученных данных о фильме (сейчас выдает информацию на английском)
    - [ ] Отправка постера фильма файлом, а не ссылкой

