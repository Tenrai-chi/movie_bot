from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime
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
    """ Таблица user """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_telegram_id = Column(BigInteger, nullable=False)
    last_request = Column(DateTime, nullable=True)
    username = Column(String(255), nullable=True)


class Request(Base):
    """ Таблица request, содержащая запросы выполненные корректно """

    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    imdbID = Column(String(50), nullable=False)
    date_time = Column(DateTime, default=datetime.utcnow)


class BadRequest(Base):
    """ Таблица bad_request, содержащая запросы выполненные с ошибками"""

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
                    username=user.username)
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
        if user is None:
            print('Получилась фигня')  # Обработать ошибку, если пользователя все таки нет в белом листе
        else:
            request = BadRequest(user_id=user_in_table.id,
                                 title=title,
                                 date_time=date_time,
                                 error=error)
            db_sess.add(request)
            db_sess.commit()
            db_sess.refresh(request)
            return request


def update_last_request(user: _user.User, date_time):
    """ Обновление поля last_request у user """

    with session_local() as db_sess:
        user = db_sess.query(User).filter(User.user_telegram_id == user.id).first()
        user.last_request = date_time
        db_sess.commit()


def session_local() -> Session:
    """ Создание сессии в SQLAlchemy """

    session = sessionmaker(bind=engine)
    return session()
