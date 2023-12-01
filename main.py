import telebot
from telebot import types
from saucenao_api import SauceNao
from urllib.parse import urlparse, parse_qs
from validators import url as urlValidator

bot_id = "telegram_bot_id"
bot = telebot.TeleBot(bot_id)
sauce_api = SauceNao("sauce_nao_id")

def find(message):
    if message.content_type == 'photo':
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            results = sauce_api.from_url("https://api.telegram.org/file/bot" + bot_id + "/" + file_info.file_path)
            number_of_result = 0
            markup = types.InlineKeyboardMarkup()

            for sauce in results:
                if sauce.similarity >= 60:
                    if len(sauce.urls) != 0:
                        for url in sauce.urls:
                            name = urlparse(url)
                            url_tmp = types.InlineKeyboardButton(name.hostname, url = url)
                            markup.add(url_tmp)
                        if 'source' in sauce.raw['data']:
                            if urlValidator(sauce.raw['data']['source']):
                                name = urlparse(sauce.raw['data']['source'])
                                url_tmp = types.InlineKeyboardButton(name.hostname, url = sauce.raw['data']['source'])
                                markup.add(url_tmp)
            if results[0].similarity >= 50:
                while results[number_of_result].author == None:
                    number_of_result = number_of_result + 1

                answer = "*Название: *" + results[number_of_result].title.replace(
                    '_', ' ').replace(
                    '*', ' ') + "\n*Автор: *" + results[number_of_result].author.replace(
                        '_', ' ').replace('*', ' ') + "\n"
                answer = answer + "\n_Если не нашлось сурса, попробуйте вручную на сайтах:_ *saucenao.com | yandex.ru/images/ | images.google.ru*" 
                bot.reply_to(message, answer, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview = True)
            else:
                answer = "К сожалению, ничего не найдено.\nМожешь попробовать сам на сайтах \n*saucenao.com | yandex.ru/images/ | images.google.ru*"
                bot.reply_to(message, answer, parse_mode="Markdown", disable_web_page_preview = True)    
        except Exception as e:
            bot.send_message(message.chat.id, 'Ой... Что-то пошло не так, попробуйте снова.\nError: ', e)
    else:
        bot.send_message(message.chat.id, 'Это не картинка...')

@bot.message_handler(commands=["start"])
def start(message, res=False):
    bot.send_message(message.chat.id, 'Пришли картинку, я попробую найти оригинал и автора')

@bot.message_handler(content_types=['photo'])
def finder(message):
    if message.chat.type == "private" or message.chat.type == "group" and message.caption == "/f":
        find(message)

@bot.message_handler(commands=["f"])
def reaction_for_answer(message):
    send = bot.send_message(message.chat.id, 'Жду фото...')
    bot.register_next_step_handler(send, find)

bot.polling(none_stop=True, interval=0)