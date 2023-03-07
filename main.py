import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

from decouple import config


anime_series = False

text: str = ''
anime_ser: str = ''
anime_name: str = ''
bot = telebot.TeleBot(token=config("TOKEN", cast=str))
url = 'https://gogoanime.consumet.stream/recent-release'
r = requests.get(url=url)
names: list = []

for i in r.json():
    names.append(i['animeTitle'])

@bot.callback_query_handler(func = lambda call: True)
def check(call):
    global names
    if call.data == 'names':
        answer = ''
        for i in names:
            answer += i+'\n'
        bot.send_message(call.message.chat.id, answer)
        bot.send_message(call.message.chat.id, 'Input name')
    if call.data == 'start':
        bot.send_message(call.message.chat.id, 'Input name of the anime')

@bot.message_handler(commands=['watch'])
def watch(message):
    bot.send_message(message.chat.id, 'Input name of the anime')

@bot.message_handler(commands=['start', 'help'])
def watch(message):
    bot.send_message(message.chat.id, 'Input /names or /watch')

@bot.message_handler(commands=['names'])
def send_names(message):
    global names
    answer = ''
    for i in names:
        answer += i+'\n'
    bot.send_message(message.chat.id, answer)
    bot.send_message(message.chat.id, 'Input name')

@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_anime = types.InlineKeyboardButton('watch', callback_data='start')
    btn_names = types.InlineKeyboardButton('names', callback_data='names')
    markup.add(btn_anime)
    markup.add(btn_names)
    bot.send_message(message.chat.id, 'Choose option', reply_markup=markup)

def check(message, link):
    global anime_series
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'lxml')
    file = str(soup.find_all('div', class_='anime_name new_series'))
    if '404 Not Found' in file:
        bot.send_message(message.chat.id, 'Anime series was not found. Try again')
        anime_series = True
    else:
        anime_series = False
        bot.send_message(message.chat.id, 'Link : '+link)

@bot.message_handler()
def mess(message: telebot.types.Message):
    global names, anime_series, anime_ser, anime_name
    if anime_series == True:
        try:
            anime_ser = int(message.text)
            print(f'anime_name : {anime_name}, anime_ser : {anime_ser}')
            if type(anime_ser) == int:
                for i in r.json():
                    if anime_name == i['animeTitle']:
                        anime_ser = str(anime_ser)
                        if len(anime_ser)>0:
                            link = str(i['episodeUrl'])
                            link = link.split('-')
                            link[-1] = anime_ser
                            link = '-'.join(link)
                            check(message, link)
        except ValueError:    
                bot.send_message(message.chat.id, 'Episode must be a number')
    else:
        anime_name = message.text
        if anime_name in names:
            for i in r.json():
                if anime_name == i['animeTitle']:
                    photo = i["animeImg"]
                    bot.send_photo(message.chat.id, photo)
                    anime_series = True
                    bot.send_message(message.chat.id, "Input episod of the anime")
        else:
            anime_series = False
            bot.send_message(message.chat.id, 'Anime series was not found. Try again.')

bot.polling(non_stop=True)