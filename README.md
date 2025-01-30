# movie_bot
Телеграм бот для получения информации о фильмах с помощью OMDb API @films_ten_bot
## Функционал
* Для доступа к боту пользователю необходимо ввести ключ с помощью команды /activate <ключ>, если пользователь попытается сделать запрос к боту не авторизовавшись, то бот уведомит его о необходимости авторизации
* Количество запросов к боту зависит от уровня подписки. base - 5, medium - 10, maximum - 50)
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
## Доступные команды:
На данный момент для взаимодействия с ботом доступны следующие команды:
- **start**: Вывод информации о боте
- **activate**: активация бота и добавление пользователя в "белый список"
- **amount**: Количество запросов за эти сутки
- **my_sub**: Информация о текущей подписке
- **subscription**: Информация о всех доступных подписках
- **buy**: В стадии разработки! Покупка подписки

## **База данных**
База данных Postgreql, взаимодействие с ней происходит через SqlAlchemy и pg8000
* Таблица user. Хранит данные о авторизированных пользователях:
  |  id  | user_telegram_id |  last_request  | username |   subscription  |
  |------|------------------|----------------|----------|-----------------|
  | auto |        int       |     datetime   |    str   | subscription.id |
      
* Таблица request. Хранит данные успешных запросах:
  |  id  | user_id |  imdbID  | date_time |
  |------|---------|----------|-----------|
  | auto | user.id | char(50) |  datetime |
    
* Таблица bad_request. Хранит данные о неуспешных запросах и вызванных ошибках:
  |  id  | user_id |   title  | date_time |    error   |
  |------|---------|----------|-----------|------------|
  | auto | user.id | char(50) |  datetime |  char(200) |

* Таблица subscription. Хранит данные о доступных подписках:
  |  id  |   name   |  msx_request  |   price   |
  |------|----------|---------------|-----------|
  | auto | char(20) |      int      |    int    |
  
## **Планируемые улучшения:**
- [ ] Запуск с помощью Docker
- [x] Подписки base, medium, maximum, которая оозначает максимальное количество запросов в сутки. 5, 10 и 50 соответственно. Base дается автоматически всем авторизованным пользователям.
- [ ] Покупка подписок с помощью бота через Telegram Payments. Команда /buy
- [ ] Запись транзакций при покупке подписок
- [ ] Перевод полученных данных о фильме (сейчас выдает информацию на английском)
- [x] Команда /my_sub - текущий уровень подписки пользователя
- [x] Команда /amount - количество запросов в сутки <успешные запросы>/<максимальное количество запросов>
- [x] Улучшение внешнего вида бота (добавление фотографии бота, вывод всех доступных команд, кнопка start при подключении к боту)

