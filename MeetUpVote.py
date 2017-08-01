import telebot

TOKEN = '339578780:_______hRxLhusZ16fGMZ5XjPdil8bw70do' # полученный у @BotFather
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
  sent = bot.send_message(message.chat.id, 'Как тебя зовут?')
  bot.register_next_step_handler(sent, hello)
  
def hello(message):
  sent = bot.send_message(
    message.chat.id, 
    'Привет, {name}. Рад тебя видеть.'.format(name=message.text))

bot.polling()  
