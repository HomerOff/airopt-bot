import ast
from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import MediaGroupFilter
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import FileIsTooBig
from aiogram_media_group import media_group_handler

from database.db import Database

from bot import bot
from handlers.state.admin_add_state import is_price
from markups import adminMenu, admin_category_list, delKeyboard, mainChoice, admin_product_list
from markups import adminEdit, check_prod_card

db = Database('database/database.db')


class AdminEdit(StatesGroup):
    prod_category = State()
    prod_name = State()
    prod_choice = State()
    prod_edit = State()
    prod_apply = State()


async def edit_admin_prod_category(message: types.Message, state: FSMContext):
    if message.text in db.get_products_category():
        async with state.proxy() as data:
            data['prod_category'] = message.text
        await bot.send_message(message.from_user.id, 'Выберите название товара',
                               reply_markup=admin_product_list(data['prod_category']))
        await AdminEdit.next()
    elif message.text == 'Фото отзывов':
        async with state.proxy() as data:
            data['prod_choice'] = message.text
            data['prod_media'] = {"video": [], "photo": []}
        await bot.send_message(message.from_user.id,
                               "Отправьте фото и видео отзывов (после отправка нажмите ✅, если фотографии нет - нажмите на кнопку 🚫)",
                               reply_markup=mainChoice)
        await AdminEdit.prod_edit.set()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное значение!',
                               reply_markup=admin_category_list())


async def edit_admin_prod_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['prod_name'] = message.text
    if message.text in db.get_products_name(data['prod_category'], all_items=True):

        await bot.send_message(message.from_user.id, 'Выберите действие с данной карточкой товара',
                               reply_markup=adminEdit)
        await AdminEdit.next()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное значение!',
                               reply_markup=admin_product_list(data['prod_category']))


async def edit_admin_prod_choice(message: types.Message, state: FSMContext):
    if is_edit(message.text):
        async with state.proxy() as data:
            data['prod_choice'] = message.text
            data['prod_media'] = {"video": [], "photo": []}
        if data['prod_choice'] == 'Категория':
            await bot.send_message(message.from_user.id,
                                   f"В настоящий момент категория {data['prod_name']}: {db.get_product_category(data['prod_name'])}",
                                   reply_markup=admin_category_list(is_edit=False))
            await bot.send_message(message.from_user.id, "Выберите категорию товара или создайте новую",
                                   reply_markup=admin_category_list(is_edit=False))
            await AdminEdit.next()
        elif data['prod_choice'] == 'Название':
            await bot.send_message(message.from_user.id, f"В настоящий момент название товара: {data['prod_name']}",
                                   reply_markup=delKeyboard)
            await bot.send_message(message.from_user.id, "Укажите новое название",
                                   reply_markup=delKeyboard)
            await AdminEdit.next()
        elif data['prod_choice'] == 'Описание':
            await bot.send_message(message.from_user.id,
                                   f"В настоящий момент описание {data['prod_name']}: {db.get_product_description(data['prod_name'])}",
                                   reply_markup=delKeyboard)
            await bot.send_message(message.from_user.id, "Укажите новое описание",
                                   reply_markup=delKeyboard)
            await AdminEdit.next()
        elif data['prod_choice'] == 'Цена':
            await bot.send_message(message.from_user.id,
                                   f"В настоящий момент цена {data['prod_name']}: {str(db.get_product_price(data['prod_name']))}",
                                   reply_markup=delKeyboard)
            await bot.send_message(message.from_user.id, "Укажите новую цену",
                                   reply_markup=delKeyboard)
            await AdminEdit.next()
        elif data['prod_choice'] == 'Фото':
            try:
                card_media = db.get_product_media(data['prod_name'])
                media = types.MediaGroup()
                media_counter = 0
                if card_media:
                    for video in card_media.get('video'):
                        media_counter += 1
                        media.attach_video(video)
                    for photo in card_media.get('photo'):
                        media_counter += 1
                        media.attach_photo(photo)
                if media_counter:
                    await bot.send_media_group(message.from_user.id, media=media)
                    await bot.send_message(message.from_user.id,
                                           f"Текущие изображения у {data['prod_name']}",
                                           reply_markup=mainChoice)
                else:
                    await bot.send_message(message.from_user.id, f"В настоящий момент у {data['prod_name']} нет фото",
                                           reply_markup=mainChoice)
            except:
                await bot.send_message(message.from_user.id, f"В настоящий момент у {data['prod_name']} нет фото",
                                       reply_markup=mainChoice)
            await bot.send_message(message.from_user.id,
                                   "Отправьте фото и видео товара (после отправка нажмите ✅, если фотографии нет - нажмите на кнопку 🚫)",
                                   reply_markup=mainChoice)
            await AdminEdit.next()
        elif data['prod_choice'] == 'Удалить товар':
            await bot.send_message(message.from_user.id, "Вы хотите удалить данную карточку?",
                                   reply_markup=mainChoice)
            await AdminEdit.prod_apply.set()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное название действия!',
                               reply_markup=adminEdit)


async def edit_admin_prod_edit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['prod_edit'] = message.text
        if data['prod_choice'] == 'Фото отзывов' or data['prod_choice'] == 'Фото':
            if len(data['prod_media'].get('photo')) + len(data['prod_media'].get('video')) < 10:
                if message.photo:
                    document_id = message.photo[0].file_id
                    file_info = await (bot.get_file(document_id))
                    photo = data['prod_media'].get('photo')
                    photo.append(file_info.file_id)
                    data['prod_media'].update({'photo': photo})
                elif message.video:
                    document_id = message.video.file_id
                    file_info = await (bot.get_file(document_id))
                    video = data['prod_media'].get('video')
                    video.append(file_info.file_id)
                    data['prod_media'].update({'video': video})
                await AdminEdit.prod_edit.set()

            else:
                await bot.send_message(message.from_user.id,
                                       "Отправлено максимальное количество меда-файлов!")

    is_correct_edit = False

    if data['prod_choice'] == 'Фото отзывов' or data['prod_choice'] == 'Фото':
        if message.text == '✅' or message.text == '🚫':
            is_correct_edit = True
        elif message.text and message.text.count('video') and message.text.count('photo'):
            async with state.proxy() as data:
                data['prod_media'] = ast.literal_eval(message.text)
            is_correct_edit = True

    if data['prod_choice'] == 'Категория' and len(message.text.encode('utf-8')) > 57:
        await bot.send_message(message.from_user.id,
                               'Название слишком длинное, измените его!',
                               reply_markup=delKeyboard)
    elif data['prod_choice'] == 'Категория':
        is_correct_edit = True

    if data['prod_choice'] == 'Название' and len(message.text.encode('utf-8')) > 59:
        await bot.send_message(message.from_user.id,
                               'Название слишком длинное, измените его!',
                               reply_markup=delKeyboard)
    elif data['prod_choice'] == 'Название' and not db.product_exists(message.text):
        is_correct_edit = True
    elif data['prod_choice'] == 'Название':
        await bot.send_message(message.from_user.id,
                               'Введите уникальное название товара. Данная позиция уже существует!',
                               reply_markup=delKeyboard)
    if data['prod_choice'] == 'Описание':
        is_correct_edit = True

    if data['prod_choice'] == 'Цена' and is_price(message.text) and float(message.text) > 0:
        is_correct_edit = True
    elif data['prod_choice'] == 'Цена':
        await bot.send_message(message.from_user.id, 'Цена должна быть больше 0!')

    if is_correct_edit:
        await bot.send_message(message.from_user.id, 'Вы подтверждаете данное измненение карточки?',
                               reply_markup=mainChoice)
        await AdminEdit.next()


@media_group_handler
async def edit_admin_prod_album(messages: List[types.Message], state: FSMContext):
    async with state.proxy() as data:
        for msg in messages:
            try:
                if msg.photo:
                    document_id = msg.photo[0].file_id
                    file_info = await (bot.get_file(document_id))
                    photo = data['prod_media'].get('photo')
                    photo.append(file_info.file_id)
                    data['prod_media'].update({'photo': photo})
                elif msg.video:
                    document_id = msg.video.file_id
                    file_info = await (bot.get_file(document_id))
                    video = data['prod_media'].get('video')
                    video.append(file_info.file_id)
                    data['prod_media'].update({'video': video})
            except FileIsTooBig:
                await bot.send_message(msg.from_user.id, 'Слишком большой видео-файл!', reply_markup=adminMenu)
    await bot.send_message(messages[-1].from_user.id, 'Вы подтверждаете данное измненение карточки?',
                           reply_markup=mainChoice)
    await AdminEdit.next()


async def edit_admin_prod_apply(message: types.Message, state: FSMContext):
    if message.text == '✅':
        async with state.proxy() as data:
            data['prod_apply'] = message.text

        if data['prod_choice'] == 'Фото отзывов':
            db.set_other_media(data['prod_choice'], data['prod_media'])
        elif data['prod_choice'] == 'Категория':
            db.set_product_category(data['prod_name'], data['prod_edit'])
        elif data['prod_choice'] == 'Название':
            db.set_product_name(data['prod_name'], data['prod_edit'])
        elif data['prod_choice'] == 'Описание':
            db.set_product_description(data['prod_name'], data['prod_edit'])
        elif data['prod_choice'] == 'Цена':
            db.set_product_price(data['prod_name'], data['prod_edit'])
        elif data['prod_choice'] == 'Фото':
            db.set_product_media(data['prod_name'], data['prod_media'])
        elif data['prod_choice'] == 'Удалить товар':
            db.del_product(data['prod_name'])

        if data['prod_choice'] == 'Название':
            await bot.send_message(message.from_user.id, 'Озанакомиться с карточкой',
                                   reply_markup=check_prod_card(data['prod_edit']))
        elif not data['prod_choice'] == 'Удалить товар' and not data['prod_choice'] == 'Фото отзывов':
            await bot.send_message(message.from_user.id, 'Озанакомиться с карточкой',
                                   reply_markup=check_prod_card(data['prod_name']))
        await bot.send_message(message.from_user.id, 'Вы успешно изменили карточку!', reply_markup=adminMenu)
        await state.finish()
    elif message.text == '🚫':
        await bot.send_message(message.from_user.id, 'Вы отменили создание карточки!', reply_markup=adminMenu)
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное значение!', reply_markup=mainChoice)


def is_edit(text):
    edits_names = ['Категория', 'Название', 'Описание', 'Цена', 'Фото', 'Удалить товар']
    if text in edits_names:
        return True
    else:
        return False


def setup(dp: Dispatcher):
    dp.register_message_handler(edit_admin_prod_category, state=AdminEdit.prod_category)
    dp.register_message_handler(edit_admin_prod_name, state=AdminEdit.prod_name)
    dp.register_message_handler(edit_admin_prod_choice, state=AdminEdit.prod_choice)
    dp.register_message_handler(edit_admin_prod_album, lambda msg: msg.media_group_id, state=AdminEdit.prod_edit, content_types=['photo', 'video'])
    dp.register_message_handler(edit_admin_prod_edit, state=AdminEdit.prod_edit,
                                content_types=['text', 'photo', 'video'])
    dp.register_message_handler(edit_admin_prod_apply, state=AdminEdit.prod_apply)
