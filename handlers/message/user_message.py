from aiogram import types, Dispatcher
from database.db import Database

from config import admin_id
from bot import bot
from markups import mainMenu

db = Database('database/database.db')


async def user_start(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f'Здравствуйте! Я бот магазина Airopt.\n'
                           f'Я отвечу на основные вопросы, которые могут у вас возникнуть. '
                           f'Если в списке нет нужного вопроса или вы хотите сразу оформить заказ, '
                           f'нажмите на кнопку «Менеджер» и пишите ваш вопрос, мы свяжемся с вами в ближайшее время".',
                           parse_mode="Markdown", reply_markup=mainMenu)


def setup(dp: Dispatcher):
    dp.register_message_handler(user_start, lambda msg: not msg.from_user.id == admin_id, commands=['start'])
