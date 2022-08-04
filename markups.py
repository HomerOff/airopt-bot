import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from config import currency, manager_link, reviews_link
from database.db import Database

db = Database('database/database.db')

# основное меню
mainMenu = InlineKeyboardMarkup()
btnCatalog = InlineKeyboardButton(f'Каталог', callback_data='menu_catalog')
btnDelivery = InlineKeyboardButton(f'Доставка и оплата', callback_data='menu_delivery')
btnReviews = InlineKeyboardButton(f'Отзывы', callback_data='menu_reviews')
btnManager = InlineKeyboardButton(f'Написать менеджеру', url=manager_link)
btnOrder = InlineKeyboardButton(f'Оформить заказ', callback_data='menu_order')

mainMenu.add(btnCatalog).add(btnDelivery).add(btnReviews).add(btnManager).add(btnOrder)

# кнопки для перехода к прошлому сообщению
btnBackMenu = InlineKeyboardButton(f'Назад', callback_data=f'menu_start')
btnBackCatalog = InlineKeyboardButton(f'Назад', callback_data=f'menu_catalog')
btnBackFullCatalog = InlineKeyboardButton(f'Назад', callback_data=f'catalog_start')

btnMenu = InlineKeyboardButton(f'Основное меню', callback_data=f'menu_start')

# Каталог
mainCatalog = InlineKeyboardMarkup()
btnFullCatalog = InlineKeyboardButton(f'Подробнее о товарах (обзоры)', callback_data=f'catalog_start')
mainCatalog.add(btnFullCatalog).add(btnManager).add(btnBackMenu)

# Доставка и оплата
mainDelivery = InlineKeyboardMarkup()
mainDelivery.add(btnManager).add(btnBackMenu)

# Оформить заказ
mainOrder = InlineKeyboardMarkup()
mainOrder.add(btnManager).add(btnCatalog).add(btnBackMenu)

# меню админа
btnAdd = KeyboardButton('Добавить')
btnEdit = KeyboardButton('Редактировать')
btnUsers = KeyboardButton('Кол-во юзеров')
btnSpam = KeyboardButton('Рассылка')
btnMainMenu = KeyboardButton('Основное меню')
adminMenu = ReplyKeyboardMarkup(resize_keyboard=True)
adminMenu.add(btnAdd, btnEdit).add(btnUsers, btnSpam).add(btnMainMenu)

# удалить кнопки
delKeyboard = ReplyKeyboardRemove()

# подтверждение действий
btnDeny = KeyboardButton('🚫')

mainDeny = ReplyKeyboardMarkup(resize_keyboard=True)
mainDeny.add(btnDeny)

btnApply = KeyboardButton('✅')
mainChoice = ReplyKeyboardMarkup(resize_keyboard=True)
mainChoice.add(btnDeny, btnApply)

# редактирование карточки
btnProductCategory = KeyboardButton('Категория')
btnProductName = KeyboardButton('Название')
btnProductDescription = KeyboardButton('Описание')
btnProductPrice = KeyboardButton('Цена')
btnProductMedia = KeyboardButton('Фото')
btnProductDel = KeyboardButton('Удалить товар')
adminEdit = ReplyKeyboardMarkup(resize_keyboard=True)
adminEdit.add(btnProductDel).add(btnProductCategory, btnProductName).add(btnProductDescription, btnProductPrice).add(
    btnProductMedia)


# список названий категорий
def catalog_list():
    catalogList = InlineKeyboardMarkup(row_width=2)
    for i, name in enumerate(db.get_products_category()):
        if not len(name.encode('utf-8')) > 57:
            catalogList.add(InlineKeyboardButton(f'{name}',
                                                 callback_data=f'catalog_{name}'))
    catalogList.add(btnMenu, btnBackCatalog)
    return catalogList


# список названий продуктов
def category_list(prod_category):
    product_names = db.get_products_name(prod_category)
    categorylist = InlineKeyboardMarkup(row_width=2)
    for name in product_names:
        if not len(name.encode('utf-8')) > 59:
            categorylist.add(
                InlineKeyboardButton(f'{name} - {str("{:.2f}".format(db.get_product_price(name)))} {currency}',
                                     callback_data=f'prod_{name}'))
        else:
            logging.info(f'У товара {name} слишком длинное название')
    return categorylist.add(btnMenu, btnBackFullCatalog)


# меню каталога
def reviews_list(media_counter):
    mainReviews = InlineKeyboardMarkup()
    btnReviewsLink = InlineKeyboardButton(f'Подробнее о товарах (обзоры)', url=reviews_link)
    btnMediaBackMenu = InlineKeyboardButton(f'Назад', callback_data=f'menu{media_counter}_start')
    return mainReviews.add(btnReviewsLink).add(btnMediaBackMenu)


# карточка
def prod_card(prod_name, media_counter):
    prodCard = InlineKeyboardMarkup(row_width=2)
    btnBackCategoryDel = InlineKeyboardButton('Назад',
                                              callback_data=f'catalog{media_counter}_{db.get_product_category(prod_name)}')
    btnMenuDel = InlineKeyboardButton(f'Основное меню', callback_data=f'menu{media_counter}_start')
    return prodCard.add(btnManager).add(btnMenuDel, btnBackCategoryDel)


# просмотр карточки для администратора
def check_prod_card(product_name):
    checkAdminCart = InlineKeyboardMarkup(row_width=1)
    btnCheck = InlineKeyboardButton(f'Посмотреть карточку',
                                    callback_data=f'prod_{product_name}')
    return checkAdminCart.add(btnCheck)


# список категорий для администратора
def admin_category_list(is_edit=True):
    categoryAdminList = ReplyKeyboardMarkup(resize_keyboard=True)
    if is_edit:
        categoryAdminList.add('Фото отзывов')
    for i, name in enumerate(db.get_products_category()):
        categoryAdminList.add(KeyboardButton(name))
    return categoryAdminList


# список названий для администратора
def admin_product_list(product_category):
    product_names = db.get_products_name(product_category, all_items=True)
    productAdminList = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in product_names:
        productAdminList.add(InlineKeyboardButton(name))
    return productAdminList
