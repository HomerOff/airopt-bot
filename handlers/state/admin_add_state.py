import ast
from typing import List

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import FileIsTooBig
from aiogram_media_group import media_group_handler

from database.db import Database

from bot import bot
from markups import adminMenu, delKeyboard, mainChoice, check_prod_card

db = Database('database/database.db')


class AdminAdd(StatesGroup):
    prod_category = State()
    prod_name = State()
    prod_description = State()
    prod_price = State()
    prod_media = State()
    prod_apply = State()


async def set_admin_prod_category(message: types.Message, state: FSMContext):
    if len(message.text.encode('utf-8')) > 57:
        await bot.send_message(message.from_user.id,
                               'Название слишком длинное, измените его!',
                               reply_markup=delKeyboard)
    else:
        async with state.proxy() as data:
            data['prod_category'] = message.text
        await bot.send_message(message.from_user.id, 'Укажите название товара', reply_markup=delKeyboard)
        await AdminAdd.next()


async def set_admin_prod_name(message: types.Message, state: FSMContext):
    if len(message.text.encode('utf-8')) > 59:
        await bot.send_message(message.from_user.id,
                               'Название слишком длинное, измените его!',
                               reply_markup=delKeyboard)
    elif not db.product_exists(message.text):
        async with state.proxy() as data:
            data['prod_name'] = message.text
        await bot.send_message(message.from_user.id, 'Укажите описание товара', reply_markup=delKeyboard)
        await AdminAdd.next()
    else:
        await bot.send_message(message.from_user.id,
                               'Введите уникальное название товара. Данная позиция уже существует!',
                               reply_markup=delKeyboard)


async def set_admin_prod_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['prod_description'] = message.text
    await bot.send_message(message.from_user.id, 'Укажите цену товара', reply_markup=delKeyboard)
    await AdminAdd.next()


async def set_admin_prod_price(message: types.Message, state: FSMContext):
    if is_price(message.text) and float(message.text) > 0:
        async with state.proxy() as data:
            data['prod_price'] = message.text
            data['prod_media'] = {"video": [], "photo": []}
        await bot.send_message(message.from_user.id,
                               'Отправьте фото и видео товара по очереди (после отправка нажмите ✅, если фотографии нет - нажмите на кнопку 🚫)',
                               reply_markup=mainChoice)
        await AdminAdd.next()
    else:
        await bot.send_message(message.from_user.id, 'Цена должна быть больше 0!')


async def set_admin_prod_media(message: types.Message, state: FSMContext):
    if message.photo or message.video:
        async with state.proxy() as data:
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
                await AdminAdd.prod_media.set()
            else:
                await bot.send_message(message.from_user.id,
                                       "Отправлено максимальное количество меда-файлов!")
    elif (message.text == '✅' or message.text == '🚫') or (message.text.count('video') and message.text.count('photo')):
        async with state.proxy() as data:
            if message.text == '🚫':
                data['prod_media'] = 0
            elif message.text.count('video') and message.text.count('photo'):
                data['prod_media'] = ast.literal_eval(message.text)
        card_text = f"Категория: {data['prod_category']}\n" \
                    f"Название: {data['prod_name']}\n" \
                    f"Описание: {data['prod_description']}\n" \
                    f"Цена: {data['prod_price']}\n"
        if data['prod_media']:
            media_counter = 0
            media = types.MediaGroup()
            for video in data['prod_media'].get('video'):
                media_counter += 1
                media.attach_video(video)
            for photo in data['prod_media'].get('photo'):
                media_counter += 1
                media.attach_photo(photo)
            if media_counter:
                await bot.send_media_group(message.from_user.id, media=media)
        await bot.send_message(message.from_user.id, card_text, reply_markup=mainChoice)
        await bot.send_message(message.from_user.id,
                               'Карточка введена верно? Для подтверждения нажмите на кнопку: "✅"',
                               reply_markup=mainChoice)
        await AdminAdd.next()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное значение!', reply_markup=mainChoice)


@media_group_handler
async def set_admin_prod_album(messages: List[types.Message], state: FSMContext):
    async with state.proxy() as data:
        for msg in messages:
            try:
                if len(data['prod_media'].get('photo')) + len(data['prod_media'].get('video')) < 10:
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
                else:
                    await bot.send_message(msg.from_user.id,
                                           "Отправлено максимальное количество меда-файлов!")
                    break
            except FileIsTooBig:
                await bot.send_message(msg.from_user.id, 'Слишком большой видео-файл!', reply_markup=adminMenu)
    card_text = f"Категория: {data['prod_category']}\n" \
                f"Название: {data['prod_name']}\n" \
                f"Описание: {data['prod_description']}\n" \
                f"Цена: {data['prod_price']}\n"
    if data['prod_media']:
        media_counter = 0
        media = types.MediaGroup()
        for video in data['prod_media'].get('video'):
            media_counter += 1
            media.attach_video(video)
        for photo in data['prod_media'].get('photo'):
            media_counter += 1
            media.attach_photo(photo)
        if media_counter:
            await bot.send_media_group(messages[-1].from_user.id, media=media)
    await bot.send_message(messages[-1].from_user.id, card_text, reply_markup=mainChoice)
    await bot.send_message(messages[-1].from_user.id,
                           'Карточка введена верно? Для подтверждения нажмите на кнопку: "✅"',
                           reply_markup=mainChoice)
    await AdminAdd.next()


async def set_admin_prod_apply(message: types.Message, state: FSMContext):
    if message.text == '✅':
        async with state.proxy() as data:
            data['prod_apply'] = message.text

        db.set_product_new(data['prod_category'], data['prod_name'], data['prod_description'],
                           data['prod_price'], data['prod_media'])

        await bot.send_message(message.from_user.id, 'Озанакомиться с карточкой',
                               reply_markup=check_prod_card(data['prod_name']))
        await bot.send_message(message.from_user.id, 'Ваша карточка успешно создана!', reply_markup=adminMenu)
        await state.finish()
    elif message.text == '🚫':
        await bot.send_message(message.from_user.id, 'Вы отменили создание карточки!', reply_markup=adminMenu)
        await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Введено некорректное значение!', reply_markup=mainChoice)


def is_price(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def setup(dp: Dispatcher):
    dp.register_message_handler(set_admin_prod_category, state=AdminAdd.prod_category)
    dp.register_message_handler(set_admin_prod_name, state=AdminAdd.prod_name)
    dp.register_message_handler(set_admin_prod_description, state=AdminAdd.prod_description)
    dp.register_message_handler(set_admin_prod_price, state=AdminAdd.prod_price)
    dp.register_message_handler(set_admin_prod_album, lambda msg: msg.media_group_id, state=AdminAdd.prod_media,
                                content_types=['photo', 'video'])
    dp.register_message_handler(set_admin_prod_media, state=AdminAdd.prod_media,
                                content_types=['text', 'photo', 'video'])
    dp.register_message_handler(set_admin_prod_apply, state=AdminAdd.prod_apply)
