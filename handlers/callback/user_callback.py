import logging

from aiogram import types, Dispatcher
from aiogram.types import CallbackQuery

from database.db import Database

from config import currency
from bot import bot
from markups import mainMenu, prod_card, category_list, catalog_list, reviews_list, mainOrder, mainDelivery
from markups import mainCatalog

db = Database('database/database.db')


async def main_menu(call: CallbackQuery):
    if not db.user_exists(call.from_user.id):
        db.add_user(call.from_user.id)

    temp, tab = call.data.split('_')

    if tab == 'start':

        if temp.removeprefix('menu'):
            try:
                for i in range(int(temp.removeprefix('menu'))):
                    await bot.delete_message(call.from_user.id, call.message.message_id - (1 + i))
            except:
                pass

        await bot.edit_message_text(f'Здравствуйте! Я бот магазина Airopt.\n'
                                    f'Я отвечу на основные вопросы, которые могут у вас возникнуть. '
                                    f'Если в списке нет нужного вопроса или вы хотите сразу оформить заказ, '
                                    f'нажмите на кнопку «Менеджер» и пишите ваш вопрос, мы свяжемся с вами в ближайшее время".',
                                    call.from_user.id, call.message.message_id,
                                    parse_mode="Markdown", reply_markup=mainMenu)

    elif tab == 'catalog':
        price_text = ''
        try:
            for i, category in enumerate(db.get_products_category()):
                price_text += f'_\n{str(i + 1)}._ *{category}:*\n\n'
                for name in db.get_products_name(category):
                    price_text += f'▪️ *{name}*: _{str("{:.2f}".format(db.get_product_price(name)))} {currency}_\n'
        except Exception as e:
            logging.error(e)
            price_text = '\nОшибка с прогрузкой прайс-листа!\n'

        await bot.edit_message_text(
            f'Ниже общий прайс на все наши товары. Более подробную информацию о конкретной позиции и видео обзор можно получить, нажав соответствующую кнопку ниже\n\n'
            f'Цены в рублях:\n'
            f'{price_text}'
            f'\n\*При покупке аксессуаров отдельно от товаров, цена выше на 500₽', call.from_user.id,
            call.message.message_id,
            parse_mode="Markdown", reply_markup=mainCatalog)

    elif tab == 'delivery':
        await bot.edit_message_text('Оплата и доставка:\n\n'
                                    '📦Доставка бесплатная (при заказе от 1500, если заказ на меньшую сумму, то доставка будет за ваш счёт)\n\n'
                                    '💶Заказ оплачивается сразу, в полном размере, переводом на банковскую карту\n\n'
                                    '✅Товар отправляется на следующий день после оплаты. Трек номер для отслеживания предоставляем\n\n'
                                    '🕐 Средний срок доставки по РФ 3-5 дней', call.from_user.id,
                                    call.message.message_id,
                                    parse_mode="Markdown", reply_markup=mainDelivery)

    elif tab == 'reviews':
        media = types.MediaGroup()
        media_counter = 0

        med = db.get_other_media('Фото отзывов')
        if med:
            for video in med.get('video'):
                media_counter += 1
                media.attach_video(video)
            for photo in med.get('photo'):
                media_counter += 1
                media.attach_photo(photo)
            if media_counter:
                try:
                    await bot.send_media_group(call.from_user.id, media=media)
                except Exception as e:
                    logging.error(e)
        try:
            await bot.delete_message(call.from_user.id, call.message.message_id)
        except Exception as e:
            logging.error(e)
        await bot.send_message(call.from_user.id,
                               'Основные отзывы оставлены в нашей группе Телеграм. '
                               'Выше представленные некоторые из них. '
                               'Подробнее можно ознакомиться с отзывами в группе',
                               reply_markup=reviews_list(media_counter), parse_mode='Markdown')

    elif tab == 'order':
        await bot.edit_message_text('Для оформления заказа необходимо написать менеджеру '
                                    '(нажать на кнопку и перейти в диалог) и указать какие товары вы хотите приобрести\n'
                                    'Он скинет вам форму для заказа и реквизиты для оплаты', call.from_user.id,
                                    call.message.message_id,
                                    parse_mode="Markdown", reply_markup=mainOrder)


async def main_catalog(call: CallbackQuery):
    temp, tab = call.data.split('_')
    if tab == 'start':
        try:
            await bot.edit_message_text('Выберите интересующую Вас категорию:', call.from_user.id, call.message.message_id,
                                        reply_markup=catalog_list(), parse_mode='Markdown')
        except Exception as e:
            await bot.answer_callback_query(call.id, 'Ошибка!')
            logging.info(e)
    else:
        if temp.removeprefix('catalog'):
            try:
                for i in range(int(temp.removeprefix('catalog'))):
                    await bot.delete_message(call.from_user.id, call.message.message_id - (1 + i))
            except:
                pass
        try:
            await bot.edit_message_text('Выберите интересующий Вас товар:', call.from_user.id,
                                        call.message.message_id,
                                        reply_markup=category_list(tab), parse_mode='Markdown')
        except Exception as e:
            await bot.answer_callback_query(call.id, 'Ошибка!')
            logging.info(e)


async def main_card(call: CallbackQuery):
    temp, prod_name = call.data.split('_')

    media = types.MediaGroup()
    media_counter = 0

    med = db.get_product_media(prod_name)
    if med:
        for video in med.get('video'):
            media_counter += 1
            media.attach_video(video)
        for photo in med.get('photo'):
            media_counter += 1
            media.attach_photo(photo)
        if media_counter:
            try:
                await bot.send_media_group(call.from_user.id, media=media)
            except Exception as e:
                logging.error(e)
    try:
        await bot.delete_message(call.from_user.id, call.message.message_id)
    except Exception as e:
        logging.error(e)
    try:
        await bot.send_message(call.from_user.id, db.get_product_description(prod_name),
                               reply_markup=prod_card(prod_name, media_counter))
    except Exception as e:
        logging.error(e)
        await bot.send_message(call.from_user.id, 'Описание товара не удалось загрузить!',
                               reply_markup=prod_card(prod_name, media_counter))


def setup(dp: Dispatcher):
    dp.register_callback_query_handler(main_menu, lambda c: c.data and c.data.startswith('menu'))
    dp.register_callback_query_handler(main_catalog, lambda c: c.data and c.data.startswith('catalog'))
    dp.register_callback_query_handler(main_card, lambda c: c.data and c.data.startswith('prod'))
