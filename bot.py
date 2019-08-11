import telebot
import re

chat_id = 73420519
receive_handler = None
happy_handler = None
state_handler = None
learn_handler = None
brain = None
bot = telebot.TeleBot('941487683:AAHQqjgZ8xZyJhurGxRZwZr0IrR9zMSF0CI')


state_regexp = '(nice|fail|wait)\|(.*)'


@bot.callback_query_handler(func=lambda call: True)
def state(message):
    global state_handler, bot

    print(message)

    k = re.search(state_regexp, message.data)
    grp1 = k.group(1)
    grp2 = k.group(2)

    bot.delete_message(message.from_user.id, message.message.message_id)

    state_handler(grp1, grp2)


@bot.message_handler(commands=['learn'])
def learn(message):
    global learn_handler
    print("Start learn")

    learn_handler()


@bot.message_handler(commands=['make_happy'])
def make_happy(message):
    global happy_handler
    print("make it happy")

    happy_time = int(message.text.split(' ')[2])
    happy_multiplier = int(message.text.split(' ')[1])

    happy_handler(happy_multiplier, happy_time)


@bot.message_handler(commands=['make_sad'])
def make_sad(message):
    global brain

    sad_time = int(message.text.split(' ')[1])
    sad_multiplier = int(message.text.split(' ')[2])

    brain.set_connection_power_modifier(sad_multiplier, sad_time)


@bot.message_handler(content_types=['text'])
def send_message(message):
    global receive_handler, chat_id

    chat_id = message.chat.id

    receive_handler(bot, message.text)


def set_handler(handler):
    global receive_handler

    receive_handler = handler


def set_happy_handler(handler):
    global happy_handler

    happy_handler = handler


def set_state_handler(handler):
    global state_handler

    state_handler = handler


def set_learn_handler(handler):
    global learn_handler

    learn_handler = handler


def set_brain(br):
    global brain

    brain = br


def send_text(text):
    global chat_id

    bot.send_message(chat_id, text)


def send_learn(text, param_id):
    global chat_id

    button_ok = telebot.types.InlineKeyboardButton(
        text="Nice",
        callback_data="nice|" + str(param_id),
    )

    button_fail = telebot.types.InlineKeyboardButton(
        text="Fail",
        callback_data="fail|" + str(param_id),
    )

    button_wait = telebot.types.InlineKeyboardButton(
        text="Wait",
        callback_data="wait|" + str(param_id),
    )

    keyboard = telebot.types.InlineKeyboardMarkup(3)
    keyboard.add(button_ok, button_fail, button_wait)

    bot.send_message(chat_id, text, reply_markup=keyboard)


def pooling():
    bot.polling()

