#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import logging
import os


from telegram import ReplyKeyboardMarkup, Bot, Update
from telegram.ext import Dispatcher, CommandHandler, ConversationHandler, RegexHandler,\
                         MessageHandler, CallbackContext, Filters, CallbackQueryHandler
from enum import Enum, auto
from src.utils import *

# Enum for conversation steps
class workflowHandler(Enum):
    PHONE = auto()
    PRICE = auto()
    CONFIRM = auto()

# Returns a pre compiled Regex pattern to ignore case
def comp(pattern):
    return re.compile(pattern, re.IGNORECASE)


def start_cmd(update: Update, context: CallbackContext):
    bot = context.bot
    welcome_message = '''
    Привет! Я - бот-помощник, с радостью помогу тебе с решением мелких бытовых проблем. Сейчас я работаю только в Москве, но скоро стану доступен по всей России 😊
    '''
    task_question = 'Какое поручение ты хочешь мне дать? Отправь мне сообщением, начинающимся со слова "Добби", например, "Добби, закажи клининг на субботу"'
    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=5, action='typing')
    time.sleep(5)
    update.message.reply_text(welcome_message)

    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
    time.sleep(3)
    update.message.reply_text(task_question)

# START: Conversation to get customer task
def task_start_handler(update: Update, context: CallbackContext):
    bot = context.bot
    context.user_data['task'] = update.message.text

    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
    time.sleep(3)
    update.message.reply_text('Спасибо за поручение! Пришли мне пожалуйста номер телефона, чтобы я мог уточнять детали и отчитываться о выполнении')

    return workflowHandler.PHONE

def phone_handler(update: Update, context: CallbackContext):
    bot = context.bot
    context.user_data['phone'] = update.message.text

    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
    time.sleep(3)
    update.message.reply_text('Супер! Какое вознаграждение ты предложишь исполнителю? Отправь число в рублях (без учета расходов на само поручение), например, 300 🤑')

    return workflowHandler.PRICE

def price_handler(update: Update, context: CallbackContext):
    bot = context.bot
    context.user_data['price'] = update.message.text

    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=2, action='typing')
    time.sleep(2)

    update.message.reply_text('Принял! Мы почти закончили 😊')
    update.message.reply_text('Остался последний шаг')

    reply_msg = {'Поручение': str(context.user_data['task']),
                 'Номер телефона': str(context.user_data['phone']),
                 'Бюджет': 'до ' + str(context.user_data['price']),
                 }
    reply_keyboard = [['✅ ДА', '❌ НЕТ']]

    bot.send_chat_action(chat_id=update.effective_chat.id, timeout=4, action='typing')
    time.sleep(4)
    update.message.reply_text('Твое задание:\n')
    update.message.reply_text(''.join(k + ': ' + v + '\n' for k, v in reply_msg.items()), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return workflowHandler.CONFIRM

def confirm_handler(update: Update, context: CallbackContext):
    bot = context.bot
    confirm = update.message.text

    if confirm == '✅ ДА':
        bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
        ws = get_sheet('1cVqI3DKrgQSRnSow1hDxpYNn2oSlx-teQhBI3KQITao')
        row = find_first_blank_row(ws)
        insert_task(context.user_data['task'], ws, row)
        insert_phone(context.user_data['phone'], ws, row)
        insert_price(context.user_data['price'], ws, row)
        context.bot.send_message(chat_id='-1001577571864', text='Новое задание от {}'.format(context.user_data['phone']))
        time.sleep(3)
        update.message.reply_text(
            'Я принял твоё поручение 🤗 Скоро тебе напишут мои друзья-люди и расскажут, что делать дальше')
    else:
        bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
        time.sleep(3)
        update.message.reply_text(
            'Видимо, что-то пошло не так 😞')
        update.message.reply_text(
            'Но это не проблема! Просто отправь сообщение, начинающееся с Добби, если снова захочешь дать мне поручение')

    return ConversationHandler.END

# END: Conversation to get customer task

def human_handler(update: Update, context: CallbackContext):
    user = update.message.from_user
    context.bot.send_message(chat_id='-1001577571864', text=str(user) + 'требуется ваша помощь')
    update.message.reply_text('Уже зову своего помощника человека!')

def cancel(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, timeout=2, action='typing')
    update.message.reply_text('Видимо, что-то пошло не так 😞')
    context.bot.send_chat_action(chat_id=update.effective_chat.id, timeout=4, action='typing')
    update.message.reply_text(
        'Но это не проблема! Просто отправь сообщение, начинающееся с Добби, если снова захочешь дать мне поручение')

    return ConversationHandler.END

def default_reply_handler(update: Update, context: CallbackContext):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, timeout=2, action='typing')
    time.sleep(2)
    update.message.reply_text('Я не знаю такой команды 😞')
    context.bot.send_chat_action(chat_id=update.effective_chat.id, timeout=3, action='typing')
    time.sleep(3)
    update.message.reply_text('Нажми /help, чтобы узнать, как я работаю')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(token=os.environ["TOKEN"])
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0)

dispatcher.add_handler(CommandHandler(['start', 'help'], start_cmd))
dispatcher.add_handler(CommandHandler('human', human_handler))

task_handler = ConversationHandler(
    entry_points=[RegexHandler(comp('^Добби.*'), task_start_handler)],
    states={
            workflowHandler.PHONE: [MessageHandler(Filters.text, phone_handler)],
            workflowHandler.PRICE: [MessageHandler(Filters.text, price_handler)],
            workflowHandler.CONFIRM: [MessageHandler(Filters.text, confirm_handler)],
            },
    fallbacks=[CommandHandler('cancel', cancel)]
)
dispatcher.add_handler(task_handler)

dispatcher.add_handler(MessageHandler(Filters.all, default_reply_handler))