import asyncio
import logging

from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot import bot

# from handlers.callback import admin_callback
from handlers.callback import user_callback
from handlers.message import user_message, admin_message
from handlers.state import admin_add_state, admin_edit_state, admin_mailing_list

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

loop = asyncio.get_event_loop()

dp = Dispatcher(bot, storage=MemoryStorage())

if __name__ == '__main__':
    admin_message.setup(dp)
    user_message.setup(dp)
    # admin_callback.setup(dp)
    user_callback.setup(dp)
    admin_add_state.setup(dp)
    admin_edit_state.setup(dp)
    admin_mailing_list.setup(dp)
    executor.start_polling(dp, loop=loop)
