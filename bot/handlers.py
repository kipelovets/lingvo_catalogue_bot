
from math import floor
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from bot.language import code_by_lang, lang_by_code

from bot.storage import TranslatorsData

cb = CallbackData("l", "user_id", "from_lang",
                  "to_lang", "prev_translator", sep="|")
from_languages = ["украинский", "русский"]


def make_cb(user_id: int, from_lang: str = "", to_lang: str = "", prev_translator: str = ""):
    to_lang = code_by_lang(to_lang) if to_lang != "" else ""
    from_lang = code_by_lang(from_lang) if from_lang != "" else ""
    return cb.new(user_id=user_id, from_lang=from_lang, to_lang=to_lang, prev_translator=prev_translator)


def format_name(user: types.User) -> str:
    return user.username if user.username != "" and user.username != None else user.full_name


def format_from_language_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    for lang in from_languages:
        keyboard.add(types.InlineKeyboardButton(
            text=lang, callback_data=make_cb(user_id, lang)))
    return keyboard


def format_from_language_message(username: str) -> str:
    return f"Привет @{username}!\nВыберите язык с которого нужно перевести"


async def echo(message: types.Message):
    await message.answer(message.text)


async def start(message: types.Message):
    await message.answer(
        format_from_language_message(format_name(message.from_user)),
        reply_markup=format_from_language_keyboard(message.from_user.id))


async def welcome(chat_member: types.ChatMemberUpdated):
    user = chat_member.new_chat_member.user
    await chat_member.bot.send_message(chat_member.chat.id,
                                       format_from_language_message(
                                           format_name(user)),
                                       reply_markup=format_from_language_keyboard(user.id))


async def select_from_language(call: types.CallbackQuery, callback_data: dict):
    user_id = int(callback_data["user_id"])
    if user_id != call.from_user.id:
        await call.answer("Вы не можете отвечать на чужое сообщение!")
        return
    await call.message.edit_text(format_from_language_message(format_name(call.from_user)), reply_markup=format_from_language_keyboard(call.from_user.id))


def make_select_language(data: TranslatorsData):
    async def select_language(call: types.CallbackQuery, callback_data: dict):
        user_id = int(callback_data["user_id"])
        if user_id != call.from_user.id:
            await call.answer("Вы не можете отвечать на чужое сообщение!")
            return
        from_lang = lang_by_code(callback_data["from_lang"])

        pairs = data.get_language_pairs(from_lang)
        pairs_list = list(pairs)
        pairs_list.sort()

        keyboard = types.InlineKeyboardMarkup()
        for i in range(0, floor(len(pairs_list)/2)):
            lang = pairs_list[i*2]
            if i*2+1 < len(pairs_list):
                second_lang = pairs_list[i*2+1]
                keyboard.add(types.InlineKeyboardButton(text=lang, callback_data=make_cb(call.from_user.id, from_lang, lang)),
                             types.InlineKeyboardButton(text=second_lang, callback_data=make_cb(call.from_user.id, from_lang, second_lang)))
            else:
                keyboard.add(types.InlineKeyboardButton(text=lang, callback_data=make_cb(
                    call.from_user.id, from_lang, lang)))

        keyboard.add(types.InlineKeyboardButton(
            text="Назад", callback_data=make_cb(call.from_user.id)))

        await call.message.edit_text(f"Привет @{format_name(call.from_user)}!\nВыбранный язык документа: {from_lang}\nТеперь выберите язык на который нужно перевести: ", reply_markup=keyboard)

    return select_language


def make_choose_translator(data: TranslatorsData):
    async def choose_translator(call: types.CallbackQuery, callback_data: dict):
        user_id = int(callback_data["user_id"])
        if user_id != call.from_user.id:
            await call.answer("Вы не можете отвечать на чужое сообщение!")
            return
        from_lang = lang_by_code(callback_data["from_lang"])
        to_lang = lang_by_code(callback_data["to_lang"])
        prev_translator = callback_data["prev_translator"]

        translator = data.find_next_translator(
            from_lang, to_lang, prev_translator)
        keyboard = types.InlineKeyboardMarkup()
        if None == translator:
            keyboard.add(types.InlineKeyboardButton(
                text="Назад", callback_data=make_cb(call.from_user.id, from_lang)))
            await call.message.edit_text(f"Привет @{format_name(call.from_user)}!\nК сожалению у нас нет переводчиков для пары {from_lang} - {to_lang}", reply_markup=keyboard)
            return

        keyboard.add(types.InlineKeyboardButton(text="Следующий переводчик",
                     callback_data=make_cb(call.from_user.id, from_lang, to_lang, translator)))
        keyboard.add(types.InlineKeyboardButton(
            "Назад", callback_data=make_cb(call.from_user.id, from_lang)))
        await call.message.edit_text(f"Привет @{format_name(call.from_user)}!\nСледующий переводчик для пары {from_lang} - {to_lang}: {translator}", reply_markup=keyboard)

    return choose_translator
