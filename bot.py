"""  Основная логика работы телеграм бота """

import api
import datetime
from configparser import ConfigParser
from telegram import Update
from telegram.ext import (ApplicationBuilder,
                          ContextTypes,
                          filters,
                          CommandHandler,
                          MessageHandler, CallbackContext)

import database

config = ConfigParser()
config.read('config.ini')
TELEGRAM_BOT_TOKEN = config['telegram']['bot_token']
ACTIVATION_CODE = config['activation']['code']


def check_user(func):  # Написать тип
    """ Декоратор, проверяющий наличие пользователя в белом листе """

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if database.is_user_in_whitelist(update.effective_user.id):
            return await func(update, context)
        else:
            await update.message.reply_text('Для доступа к боту, отправьте команду /activate <код>')
    return wrapper


@check_user
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /start """

    await update.message.reply_text('Введите название фильма для поиска. '
                                    'Для более точного поиска можете ввести и год выпуска')


async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /activate """

    code = context.args[0] if context.args else None
    if code == ACTIVATION_CODE:
        user = update.effective_user
        if not database.is_user_in_whitelist(user.id):
            db_sess = database.session_local()
            try:
                database.add_user_whitelist(db_sess, user)
                await update.message.reply_text('Успешно активировано!\n'
                                                'Введите название фильма для поиска')
            except Exception as _:
                await update.message.reply_text('Успешно активировано, но не удалось получить данные о пользователе!')
            finally:
                db_sess.close()
        else:
            await update.message.reply_text('Вы уже имеете доступ к боту.'
                                            'Введите название фильма для поиска'
                                            )
    else:
        await update.message.reply_text(f'Неверный код активации')


@check_user
async def my_sub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /my_sub """

    user = update.effective_user
    name, max_request = database.get_sub_user(user)
    await update.message.reply_text(f'Статус подписки: {name}\n'
                                    f'Количество возможных запросов: {max_request}\n'
                                    'Посмотреть количество текущих запросов: /amount')


@check_user
async def amount_request_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /amount """

    user = update.effective_user
    amount_request = database.amount_request_user(user)
    max_request = database.get_max_request(user)
    await update.message.reply_text(f'Количество запросов в сутки {amount_request}/{max_request}')


@check_user
async def buy_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /buy """

    await update.message.reply_text(f'Функционал разрабатывается')


@check_user
async def subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ /subscriptions

    """

    user = update.effective_user
    pass
    # amount_request = database.amount_request_user(user)  # Добавить максю количество запросов
    await update.message.reply_text(f'')


@check_user
async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Обрабатывает сообщения с названием фильма """

    text = update.message.text
    parts = text.split()  # Разделение на слова
    if len(parts) >= 2:
        # Если название имеет хотя бы 2 слова (может быть и без года)
        title = parts[:-1]
        year = parts[-1]
        # Проверка последнего слова, что это год
        try:
            if 1900 <= int(year) <= 2025:  # Если это год
                title = ' '.join(title)
                answer = await api.search_movie_data(title, year)
        except ValueError:  # Если это часть названия
            title = text
            answer = await api.search_movie_data(title)
    # Если название фильма содержит 1 слова без даты
    else:
        title = text
        answer = await api.search_movie_data(title)
    if answer["error"] is None:
        await update.message.reply_text(answer['data'])
        # Запись в request
        date_time = datetime.datetime.now()
        database.add_request(user=update.effective_user,
                             imdb_id=answer['imdbID'],
                             date_time=date_time)
        database.update_last_request(user=update.effective_user, date_time=date_time)
    else:
        await update.message.reply_text(answer['error'])
        # Запись в bad_request
        date_time = datetime.datetime.now()
        database.add_bad_request(user=update.effective_user,
                                 title=text,
                                 date_time=date_time,
                                 error=answer['error'])
        database.update_last_request(user=update.effective_user, date_time=date_time)

    output = f'[{date_time.strftime("%Y-%m-%d %H:%M:%S")}] | {update.effective_user.id} | ' \
             f'{title} | {answer["response"]} | {answer["error"]}'
    print(output)


def main() -> None:
    """ Запуск бота """

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    activate_handler = CommandHandler('activate', activate)
    subscriptions_handler = CommandHandler('subscriptions', subscriptions)
    buy_subscriptions_handler = CommandHandler('buy', buy_subscription)
    my_sub_handler = CommandHandler('my_sub', my_sub)
    amount_request_user_handler = CommandHandler('amount', amount_request_user)
    search_movie_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie)

    application.add_handler(start_handler)
    application.add_handler(activate_handler)
    application.add_handler(my_sub_handler)
    application.add_handler(subscriptions_handler)
    application.add_handler(buy_subscriptions_handler)
    application.add_handler(amount_request_user_handler)
    application.add_handler(search_movie_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
