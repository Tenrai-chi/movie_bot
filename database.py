""" Логика работы с базой данных Postgresql """

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime, timedelta
from configparser import ConfigParser
from telegram import _user

config = ConfigParser()
config.read('config.ini')
db_host = config['postgresql']['host']
db_name = config['postgresql']['name']
db_user = config['postgresql']['user']
db_password = config['postgresql']['password']

# Создание базы данных
DATABASE_URL = f'postgresql+pg8000://{db_user}:{db_password}@{db_host}/{db_name}'
engine = create_engine(DATABASE_URL)
Base = declarative_base()


class User(Base):
    """ Таблица user.
        Хранит информацию об авторизированных пользователях:
            - Телеграм id
            - Username
            - Время последнего запроса
            - Уровень подписки
    """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(BigInteger, nullable=False)
    last_request = Column(DateTime, nullable=True)
    username = Column(String(255), nullable=True)
    subscription = Column(Integer, ForeignKey('subscription.id'))


# class Transaction(Base):
#     """ Таблица transaction.
#         Хранит информацию об транзакциях:
#     """
#
#     pass


class Subscription(Base):
    """ Таблица subscription.
        Хранит информацию о подписках:
            - Название
            - Количество максимальных запросов
            - Цена в рублях
    """

    __tablename__ = 'subscription'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    max_request = Column(Integer)
    price = Column(Integer)


class Request(Base):
    """ Таблица request.
        Содержит информацию о запросах, выполненных корректно:
            - user id из таблицы user
            - imdbID запрашиваемого фильма
            - Дата и время запроса
    """

    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    imdbID = Column(String(50), nullable=False)
    date_time = Column(DateTime, default=datetime.utcnow)


class BadRequest(Base):
    """ Таблица bad_request.
        Содержит информацию о запросах, выполненных с ошибками:
        - user id из таблицы user
        - Текст запроса
        - Дата и время запроса
        - Полученные ошибки
    """

    __tablename__ = 'bad_request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    title = Column(String(50), nullable=False)
    date_time = Column(DateTime, default=datetime.utcnow)
    error = Column(String(200), nullable=False)


def create_tables() -> None:
    """ Создание таблиц в базе данных """

    try:
        Base.metadata.create_all(engine)
        print('Таблицы успешно созданы')
    except Exception as e:
        print(f'Произошла ошибка при создании таблиц: {e}')


def add_user_whitelist(db: Session, user: _user,  last_request: datetime = None) -> User:  # user тип
    """ Добавление пользователя в белый лист """

    new_user = User(user_telegram_id=user.id,
                    last_request=last_request,
                    username=user.username,
                    subscription=1)  # Возможно поменять
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def is_user_in_whitelist(telegram_id: int) -> bool:
    """ Проверка наличия пользователя в белом листе """

    with session_local() as db_sess:
        return db_sess.query(User).filter(User.user_telegram_id == telegram_id).first() is not None


def add_request(user: _user, imdb_id: str, date_time: datetime) -> Request:
    """ Добавление записи в request """

    with session_local() as db_sess:
        user_in_table = db_sess.query(User).filter(User.user_telegram_id == user.id).first()
        if user is None:
            pass  # Обработать ошибку, если пользователя все таки нет в белом листе
        else:
            request = Request(user_id=user_in_table.id,
                              imdbID=imdb_id,
                              date_time=date_time)
            db_sess.add(request)
            db_sess.commit()
            db_sess.refresh(request)
            return request


def add_bad_request(user: _user, title, date_time: datetime, error: str) -> BadRequest:
    """ Добавление записи в bad_request """

    with session_local() as db_sess:
        user_in_table = db_sess.query(User).filter(User.user_telegram_id == user.id).first()
        request = BadRequest(user_id=user_in_table.id,
                             title=title,
                             date_time=date_time,
                             error=error)
        db_sess.add(request)
        db_sess.commit()
        db_sess.refresh(request)
        return request


def update_last_request(user: _user, date_time: datetime) -> None:
    """ Обновление поля last_request у user """

    with session_local() as db_sess:
        user = db_sess.query(User).filter(User.user_telegram_id == user.id).first()
        user.last_request = date_time
        db_sess.commit()


def session_local() -> Session:
    """ Создание сессии в SQLAlchemy """

    session = sessionmaker(bind=engine)
    return session()


def view_all_sub() -> dict:
    """ Все доступные подписки """

    with session_local() as sess:
        subs = sess.query(Subscription).all()
        subs_dict = {}
        for sub in subs:
            subs_dict[sub.name] = {
                'max_request': sub.max_request,
                'price': sub.price
            }
    return subs_dict


def get_max_request(user: _user) -> int:
    """ Максимальное количество запросов в сутки пользователя """

    with session_local() as sess:
        user, subscription = (sess.query(User, Subscription)
                              .join(Subscription, User.subscription == Subscription.id)
                              .filter(User.user_telegram_id == user.id)
                              .first())
        return subscription.max_request


def get_sub_user(user: _user) -> tuple:
    """ Информация о подписке пользователя """

    with session_local() as sess:
        user, subscription = (sess.query(User, Subscription)
                              .join(Subscription, User.subscription == Subscription.id)
                              .filter(User.user_telegram_id == user.id)
                              .first())
        return subscription.name, subscription.max_request


def amount_request_user(user: _user) -> int:
    """ Информация о количестве запросов пользователя за эти сутки """

    with session_local() as sess:
        time_threshold = datetime.now() - timedelta(days=1)
        user = sess.query(User).filter(User.user_telegram_id == user.id).first()
        amount_request = sess.query(Request).filter(Request.user_id == user.id,
                                                    Request.date_time >= time_threshold
                                                    ).count()
        return amount_request


def amount_request_for_day() -> int:
    """ Количество выполненных запросов за сутки """

    with session_local() as sess:
        time_threshold = datetime.now() - timedelta(days=1)
        amount = (sess.query(Request)
                  .filter(Request.date_time >= time_threshold)
                  .count())
        return amount
