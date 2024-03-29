import random
from typing import Optional, TypeVar, Callable, Any, Tuple

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from bot.language import code_by_lang, UA, RU, popular_pairs

from_languages = [UA, RU]
LINGVO_BOT_URL = "https://t.me/lingvo_catalogue_bot"
MOOVA_BOT_URL = "https://t.me/moovaBot"
ADMIN_URL = "https://t.me/kipelovets"


class LingvoCallbackData(CallbackData, prefix="l", sep="|"):
    user_id: int
    from_lang: Optional[str]
    to_lang: Optional[str]


class FinishCallbackData(CallbackData, prefix="f", sep="|"):
    user_id: int
    from_lang: Optional[str]


class RestartCallbackData(CallbackData, prefix="r", sep="|"):
    user_id: int
    from_lang: Optional[str]


class TranslatorCallbackData(CallbackData, prefix="t", sep="|"):
    user_id: int
    from_lang: str
    to_lang: str
    prev_translator: Optional[str] = None
    seed: int


def make_cb(
        user_id: int,
        from_lang: str | None = None,
        to_lang: str | None = None):
    to_lang = code_by_lang(to_lang) if to_lang is not None else ""
    from_lang = code_by_lang(from_lang) if from_lang is not None else ""
    return LingvoCallbackData(
        user_id=user_id,
        from_lang=from_lang,
        to_lang=to_lang
    )


def format_name(user: types.User) -> str:
    return user.username if user.username != "" and user.username is not None else user.full_name


def format_from_language_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lang in from_languages:
        builder.button(
            text=lang, callback_data=make_cb(user_id, from_lang=lang))
    builder.adjust(1)
    return builder.as_markup()


def make_seed() -> int:
    return random.randint(0, 99999)


def format_start_message_keyboard(user_id: int,
                                  button_other: str,
                                  button_no: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    seed = make_seed()
    for pair, languages in popular_pairs.items():
        from_lang, to_lang = languages
        builder.button(text=pair, callback_data=TranslatorCallbackData(
            user_id=user_id,
            from_lang=code_by_lang(from_lang),
            to_lang=code_by_lang(to_lang),
            seed=seed))
    builder.button(text=button_other, callback_data=make_cb(user_id))
    builder.button(text=button_no,
                   callback_data=FinishCallbackData(user_id=user_id,
                                                    from_lang=code_by_lang(RU)))
    builder.adjust(1)
    return builder.as_markup()


def format_welcome_message_keyboard(
        button_text: str,
        button_voice: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=button_text, url=LINGVO_BOT_URL)
    builder.button(text=button_voice, url=MOOVA_BOT_URL)
    builder.adjust(1)
    return builder.as_markup()


def format_finish_keyboard(
        user_id: int,
        from_lang: str,
        button_restart: str) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=button_restart,
                   callback_data=RestartCallbackData(user_id=user_id, from_lang=from_lang))
    builder.adjust(1)
    return builder.as_markup()


T = TypeVar('T')


def extract_kwargs(*kwarg_names: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Tuple[Any], **kwargs: Any) -> T:
            for kwarg_name in kwarg_names:
                if kwarg_name in kwargs:
                    value = kwargs.pop(kwarg_name)
                    args += (value,)
            return func(*args, **kwargs)
        return wrapper
    return decorator
