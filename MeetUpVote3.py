import telebot
import sqlite3
from telebot import types

class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
    def close(self):
        self.connection.close()
        
TOKEN = '339578780:AAH9qyjhRxLhusZ16fGMZ5XjPdil8bw70do' # полученный у @BotFather
database_name = 'MeetUpVote.db'
MEETUP_TIMEOUT = '7200'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
  sent = bot.send_message(message.chat.id, 'Привет! Как тебя зовут?')
  bot.register_next_step_handler(sent, hello)
def hello(m):
  db_worker = SQLighter(database_name)
  db_worker.cursor.execute("INSERT into User (StartTime,chat_id,tel_user_id,tel_first_name,tel_last_name,tel_username,tel_lag_code,nic) VALUES(CURRENT_TIMESTAMP,(?),(?),(?),(?),(?),(?),(?))",
    (m.chat.id, m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, m.from_user.language_code, m.text,)).fetchall()
  db_worker.connection.commit()
  Meet = db_worker.cursor.execute("SELECT * FROM MeetUp WHERE ((strftime('%s','now') - strftime('%s',StartMeetUp)) < {time}) order by StartMeetUp desc".format(time=MEETUP_TIMEOUT)).fetchall()
  if Meet:
    bot.send_message(m.chat.id, 'Спасибо {nic}, вы зарегистрированы на встрече {name}.'.format(nic=m.text,name=Meet[0][2]))
  else:
    bot.send_message(m.chat.id, 'Спасибо, но актиной встречи нет.')    
  db_worker.close()  
  
@bot.message_handler(commands=['master'])
def master(message):
  sent = bot.send_message(message.chat.id, 'Как назовем встречу?')
  bot.register_next_step_handler(sent, MeetUpName)
def MeetUpName(message):
  db_worker = SQLighter(database_name)
  db_worker.cursor.execute("INSERT into MeetUp (StartMeetUp, MasterUser, MeetUpName) VALUES(CURRENT_TIMESTAMP,(?),(?))", 
    (message.chat.id,message.text,)).fetchall()
  if db_worker.cursor.lastrowid:
    bot.send_message(message.chat.id, 'Встреча, {name} создана. id={id}'.format(name=message.text, id=db_worker.cursor.lastrowid))
  else:
    bot.send_message(message.chat.id, 'Что-то пошло не так. Повтори создание встречи')
  db_worker.connection.commit()
  db_worker.close()  

@bot.message_handler(commands=['contact'])
def get_contact(message):
  db_worker = SQLighter(database_name)
  Meet = db_worker.cursor.execute("SELECT rowid,* FROM MeetUp WHERE ((strftime('%s','now') - strftime('%s',StartMeetUp)) < {time}) order by StartMeetUp desc".format(time=MEETUP_TIMEOUT)).fetchall()
  if Meet:
    Users = db_worker.cursor.execute("SELECT u.* FROM User u, MeetUp m WHERE (u.StartTime > m.StartMeetUp) and (m.rowid = {mid})".format(mid=Meet[0][0])).fetchall()
    if Users:
      for u in Users:
        if (u[1] != message.chat.id) and (message.chat.id == Meet[0][2]):
          keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
          button_phone = types.KeyboardButton(text="Отправить свой контакт", request_contact=True)
          keyboard.add(button_phone)
          send = bot.send_message(u[1], "Для участия в мероприятии {mt} нажмите на кнопку «Отправить свой контакт».".format(mt=Meet[0][3]), reply_markup=keyboard)
          bot.register_next_step_handler(send, SaveContact)
    else:
      bot.send_message(message.chat.id, 'Нет зарегистрированных посетителей') 
  else:
    bot.send_message(message.chat.id, 'Просьба зарегистрировать на встрече командой /start')    
  db_worker.close()  
  
def SaveContact(c):
#  print(c)
  db_worker = SQLighter(database_name)  
  Meet = db_worker.cursor.execute("SELECT rowid,* FROM MeetUp WHERE ((strftime('%s','now') - strftime('%s',StartMeetUp)) < {time}) order by StartMeetUp desc".format(time=MEETUP_TIMEOUT)).fetchall()
  db_worker.cursor.execute("Update user Set sel_number='{ph}' WHERE chat_id={cid}".format(ph=c.contact.phone_number,cid=c.chat.id)).fetchall()
  bot.send_message(Meet[0][2], 'Сохранили контакт {f} {i} тел: {t}'.format(f=c.contact.first_name,i=c.contact.last_name,t=c.contact.phone_number))
  db_worker.connection.commit()
  db_worker.close()  
  
@bot.message_handler(func=lambda m: True)
def echo_all(message):
  db_worker = SQLighter(database_name)
  Meet = db_worker.cursor.execute("SELECT rowid,* FROM MeetUp WHERE ((strftime('%s','now') - strftime('%s',StartMeetUp)) < {time}) order by StartMeetUp desc".format(time=MEETUP_TIMEOUT)).fetchall()
  if Meet:
    Users = db_worker.cursor.execute("SELECT u.* FROM User u, MeetUp m WHERE (u.StartTime > m.StartMeetUp) and (m.rowid = {mid})".format(mid=Meet[0][0])).fetchall()
    if Users:
      for u in Users:
        if (u[1] != message.chat.id) and (message.chat.id == Meet[0][2]):
          bot.send_message(u[1], Meet[0][3] + ": " + message.text)
        elif (message.chat.id != Meet[0][2]) and (u[1] == message.chat.id):
          bot.send_message(Meet[0][2], u[7] +': '+ message.text)
    else:
      bot.send_message(message.chat.id, 'Нет зарегистрированных посетителей') 
  else:
    bot.send_message(message.chat.id, 'Просьба зарегистрировать на встрече командой /start')    
  db_worker.close()  

bot.polling()  