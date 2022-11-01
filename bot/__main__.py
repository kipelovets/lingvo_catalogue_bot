import logging
import os
import sys

from aiogram import Bot, Dispatcher, executor, types

from bot.messages import load_messages
from .storage import load
from .dispatcher import configure_dispatcher
from .handlers import Handler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    token = os.getenv('TELEGRAM_TOKEN')
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_name = os.getenv('AIRTABLE_TABLE_NAME')
    messages_table_name = os.getenv('AIRTABLE_MESSAGES_TABLE_NAME')
    if token is None or api_key is None or base_id is None or table_name is None or \
            messages_table_name is None:
        print("Error: required env vars not defined")
        sys.exit(1)

    bot = Bot(token=token)
    dispatcher = Dispatcher(bot)

    data = load(api_key, base_id, table_name)
    messages = load_messages(api_key, base_id, messages_table_name)
    handler = Handler(data, messages)
    reloader = make_reloader(handler, api_key, base_id, table_name, messages_table_name)
    configure_dispatcher(dispatcher, handler, reloader)

    executor.start_polling(
        dispatcher,
        allowed_updates=types.AllowedUpdates.MESSAGE +
        types.AllowedUpdates.CALLBACK_QUERY +
        types.AllowedUpdates.CHAT_MEMBER)


def make_reloader(handler: Handler, api_key, base_id, table_name, messages_table_name):
    async def reloader(message: types.Message):
        handler.data = load(api_key, base_id, table_name)
        handler.messages = load_messages(api_key, base_id, messages_table_name)
        await message.answer("Done")
    return reloader


if __name__ == "__main__":
    main()
