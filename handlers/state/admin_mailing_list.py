from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database.db import Database

from bot import bot
from markups import adminMenu, mainChoice

db = Database('database/database.db')


class AdminMailingList(StatesGroup):
    admin_message = State()
    admin_apply = State()


async def set_admin_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_message'] = message.md_text
        data['file_id'] = 0
        if message.photo:
            document_id = message.photo[0].file_id
            file_info = await (bot.get_file(document_id))
            data['file_id'] = file_info.file_id
    await AdminMailingList.next()
    await bot.send_message(message.from_user.id, 'Выполнить данное действие?', reply_markup=mainChoice)


async def set_admin_apply(message: types.Message, state: FSMContext):
    if message.text == '✅':
        async with state.proxy() as data:
            data['user_apply'] = message.text
        await bot.send_message(message.from_user.id, 'Сообщения отправляются, ожидайте...',
                               reply_markup=types.ReplyKeyboardRemove())
        user_count = 0
        for user in db.get_users():
            try:
                if data['file_id']:
                    await bot.send_photo(user[0], data['file_id'], caption=data['user_message'],
                                         parse_mode="MarkdownV2")
                else:
                    await bot.send_message(user[0], data['user_message'], parse_mode="MarkdownV2")
                user_count += 1
            except:
                # await bot.send_message(message.from_user.id, f'Юзер с ID {str(user[0])} не найден!')
                continue
        await bot.send_message(message.from_user.id, f'Сообщение было отправлено всем пользователям!\n'
                                                     f'Количество отправленных сообщений: {str(user_count)}',
                               reply_markup=adminMenu)
    else:
        await bot.send_message(message.from_user.id, 'Сообщение НЕ было отправлено!', reply_markup=adminMenu)
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(set_admin_message, state=AdminMailingList.admin_message, content_types=['text', 'photo'])
    dp.register_message_handler(set_admin_apply, state=AdminMailingList.admin_apply)
