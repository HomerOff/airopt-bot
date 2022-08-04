from typing import List

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import FileIsTooBig
from aiogram_media_group import media_group_handler

from database.db import Database

from config import admin_id
from bot import bot
from handlers.message.user_message import user_start
from handlers.state.admin_add_state import AdminAdd
from handlers.state.admin_edit_state import AdminEdit
from handlers.state.admin_mailing_list import AdminMailingList
from markups import adminMenu, admin_category_list

db = Database('database/database.db')


async def admin_start(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    await bot.send_message(admin_id, 'Здравствуйте. Вы вошли в качестве Администратора.', reply_markup=adminMenu)


async def admin_menu(message: types.Message):
    if message.text == 'Добавить':
        await bot.send_message(message.from_user.id, "Выберите категорию товара или создайте новую",
                               reply_markup=admin_category_list(is_edit=False))
        await AdminAdd.prod_category.set()
    elif message.text == 'Редактировать':
        await bot.send_message(message.from_user.id, "Выберите категорию",
                               reply_markup=admin_category_list())
        await AdminEdit.prod_category.set()
    elif message.text == 'Кол-во юзеров':
        await bot.send_message(message.from_user.id, f"Количество пользователей: {db.get_count_users()}",
                               reply_markup=adminMenu)
    elif message.text == 'Рассылка':
        await bot.send_message(message.from_user.id, "Укажите сообщение, которое будет отправлено всем пользователям: ")
        await AdminMailingList.admin_message.set()
    elif message.text == 'Основное меню':
        await user_start(message)
    else:
        await bot.send_message(message.from_user.id, 'Некорректная команда!', reply_markup=adminMenu)

@media_group_handler
async def admin_album(messages: List[types.Message]):
    album = {"video": [], "photo": []}
    for msg in messages:
        try:
            if msg.photo:
                document_id = msg.photo[0].file_id
                file_info = await (bot.get_file(document_id))
                photo = album.get('photo')
                photo.append(file_info.file_id)
                album.update({'photo': photo})
            elif msg.video:
                document_id = msg.video.file_id
                file_info = await (bot.get_file(document_id))
                video = album.get('video')
                video.append(file_info.file_id)
                album.update({'video': video})
        except FileIsTooBig:
            await bot.send_message(msg.from_user.id, 'Слишком большой видео-файл!', reply_markup=adminMenu)

    await bot.send_message(messages[-1].from_user.id, f'{str(album)}', reply_markup=adminMenu)


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_start, lambda msg: msg.from_user.id == admin_id, commands=['start'])
    dp.register_message_handler(admin_menu, lambda msg: msg.from_user.id == admin_id, content_types=['text'])
    dp.register_message_handler(admin_album, lambda msg: msg.from_user.id == admin_id, content_types=['photo', 'video'])
