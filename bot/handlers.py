
import logging
from telegram import Update
from telegram.ext import (Updater, CallbackContext, CommandHandler)


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Hello, I'm a bot")

def delete_join_messages():
    pass

def delete_leave_messages():
    pass

def delete_bots():
    pass

def ban_bot_inviters():
    pass

def ban_arabic_usernames():
    pass

def delete_arabic_messages():
    pass

def ban_if_first_message_has_links():
    pass

def welcome_message():
    pass

def chat_member(update: Update, context: CallbackContext):
    
    user = update.chat_member.new_chat_member.user
    logging.debug(f"chat member id={user.id} fname={user.first_name} lname={user.last_name} uname={user.username} is_bot={user.is_bot}")

def my_member(update: Update, context: CallbackContext):
    user = update.chat_member.new_chat_member.user
    logging.debug(f"MY chat member id={user.id} fname={user.first_name} lname={user.last_name} uname={user.username} is_bot={user.is_bot}")
