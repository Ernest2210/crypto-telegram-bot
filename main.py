import json
import _thread
import time
import telebot
from telebot import types
import PriceParser
import NewsParser
from Variables import TOKEN, users, parse_delay

bot = telebot.TeleBot(TOKEN)

#регистрация пользователей(добавление информации о пользователях в хэшь таблицу с ключом- id пользователя в телеграме и value - выбранный язык и время поста последней просмотренной статьи)
def register_user(message, language="en", state=0):
    users[str(message.chat.id)] = [language, state]

#функция для парсинга новостей каждые parse_delay секунд(запускается в отдельном потоке)
def send_news():
    while True:
        time.sleep(parse_delay)
        #парсинг доступных новостей на каждом из языков
        uk_articles = NewsParser.get_articles('uk')
        ua_articles = NewsParser.get_articles('ua')
        pl_articles = NewsParser.get_articles('pl')
        for key in users.keys():
            data, max_time = NewsParser.news_parse(users[key], uk_articles, ua_articles, pl_articles)
            users[key][1]= max_time
            for text in data:
                bot.send_message(key, text, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    if users.get(str(message.chat.id)) == None:
        register_user(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('PL'+'\U0001F1F5'+'\U0001F1F1')
    item2 = types.KeyboardButton('UA'+'\U0001F1FA'+'\U0001F1E6')
    item3 = types.KeyboardButton('UK'+'\U0001F1EC'+'\U0001F1E7')


    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Hello, please select a language'.format(message.from_user), reply_markup= markup)

#При нажатиии InlineButtons (Bitcoin Etherium, USDT) запускается данная функция для парсинга цен
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
   try:
       if call.message:
           #в зависимости от языка отправляются разные данные
           # (Пример: при нажатии на кнопку биткоин с польским языком отправляется btc_pl),
           # в данном блоке условий определяется на каком языке будет меню пользователя после отправки цены монеты
           if str(call.data).endswith("pl"):
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               item1 = types.KeyboardButton('CENA' + '\U0001F4B8')
               item2 = types.KeyboardButton('WIADOMOŚCI' + '\U0001F5DE')
               item3 = types.KeyboardButton('POOL' + '\U0001F50C')
               markup.add(item1, item2, item3)
           elif str(call.data).endswith("ua"):
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               item1 = types.KeyboardButton('ЦІНА' + '\U0001F4B8')
               item2 = types.KeyboardButton('НОВИНИ' + '\U0001F5DE')
               item3 = types.KeyboardButton('ПУЛ' + '\U0001F50C')
               markup.add(item1, item2, item3)
           elif str(call.data).endswith("uk"):
               markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
               item1 = types.KeyboardButton('PRICE' + '\U0001F4B8')
               item2 = types.KeyboardButton('NEWS' + '\U0001F5DE')
               item3 = types.KeyboardButton('POOLING' + '\U0001F50C')
               markup.add(item1, item2, item3)

            #данный блок кода запускает парсер выбранной монеты и отправляет сообщение с ценой пользователю
           if str(call.data).startswith("btc_"):
               answer = "BTC/USD " + PriceParser.get_btc_price() + "$"
               bot.send_message(call.message.chat.id, answer.format(call.message.from_user), reply_markup= markup)

           elif str(call.data).startswith("eth_"):
               answer = "ETH/USD " + PriceParser.get_eth_price() + "$"
               bot.send_message(call.message.chat.id, answer.format(call.message.from_user), reply_markup=markup)

           elif str(call.data).startswith("usdt_"):
               answer = "USDT/USD " + PriceParser.get_usdt_price() + "$"
               bot.send_message(call.message.chat.id, answer.format(call.message.from_user), reply_markup=markup)

   except Exception as e:
       print(repr(e))

@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        #Start page (select language)
        if message.text == 'PL'+'\U0001F1F5'+'\U0001F1F1':
            # в случае если пользователь не зарегестрирован(его нет в хеш-таблице users)
            # данного пользователя регестрируют и вписывают выбранный им язык.
            # Если пользователь уже был зарегестрирован, то в хеш-таблице изменяется информация о языке (в данном случае польский)
            if users.get(str(message.chat.id)) == None:
                register_user(message, "pl")
            else:
                users[str(message.chat.id)][0] = "pl"


            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('CENA' + '\U0001F4B8')
            item2 = types.KeyboardButton('WIADOMOŚCI' + '\U0001F5DE')
            item3 = types.KeyboardButton('POOL' + '\U0001F50C')

            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Wybierz sekcję'.format(message.from_user), reply_markup= markup)

        elif message.text == 'UA'+'\U0001F1FA'+'\U0001F1E6':
            # в случае если пользователь не зарегестрирован(его нет в хеш-таблице users)
            # данного пользователя регестрируют и вписывают выбранный им язык.
            # Если пользователь уже был зарегестрирован, то в хеш-таблице изменяется информация о языке (в данном случае украинский)
            if users.get(str(message.chat.id)) == None:
                register_user(message, "ua")
            else:
                users[str(message.chat.id)][0] = "ua"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('ЦІНА' + '\U0001F4B8')
            item2 = types.KeyboardButton('НОВИНИ' + '\U0001F5DE')
            item3 = types.KeyboardButton('ПУЛ' + '\U0001F50C')

            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Вибери розділ'.format(message.from_user), reply_markup=markup)

        elif message.text == 'UK'+'\U0001F1EC'+'\U0001F1E7':
            # в случае если пользователь не зарегестрирован(его нет в хеш-таблице users)
            # данного пользователя регестрируют и вписывают выбранный им язык.
            # Если пользователь уже был зарегестрирован, то в хеш-таблице изменяется информация о языке (в данном случае английский)
            if users.get(str(message.chat.id)) == None:
                register_user(message, "uk")
            else:
                users[str(message.chat.id)][0] = "uk"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('PRICE' + '\U0001F4B8')
            item2 = types.KeyboardButton('NEWS' + '\U0001F5DE')
            item3 = types.KeyboardButton('POOLING' + '\U0001F50C')

            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Select a section'.format(message.from_user), reply_markup=markup)

        #выбор раздела
        elif message.text == 'DO WYBORU SEKCJI':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('CENA' + '\U0001F4B8')
            item2 = types.KeyboardButton('WIADOMOŚCI' + '\U0001F5DE')
            item3 = types.KeyboardButton('POOL' + '\U0001F50C')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Wybierz sekcję'.format(message.from_user), reply_markup= markup)

        elif message.text == 'ВИБІР РОЗДІЛУ':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('ЦІНА' + '\U0001F4B8')
            item2 = types.KeyboardButton('НОВИНИ' + '\U0001F5DE')
            item3 = types.KeyboardButton('ПУЛ' + '\U0001F50C')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Вибери розділ'.format(message.from_user), reply_markup= markup)

        elif message.text == 'SELECTING A SECTION':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('PRICE' + '\U0001F4B8')
            item2 = types.KeyboardButton('NEWS' + '\U0001F5DE')
            item3 = types.KeyboardButton('POOLING' + '\U0001F50C')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Select a section'.format(message.from_user), reply_markup= markup)


        # Цены (отправляется сообщение с предложением выбрать тикер монеты (три InlineButton bitcoin, etherium, usdt))
        elif message.text == 'CENA' + '\U0001F4B8':
            inline = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('BITCOIN', callback_data="btc_pl")
            item2 = types.InlineKeyboardButton('ETHEREUM', callback_data="eth_pl")
            item3 = types.InlineKeyboardButton('USDT', callback_data="usdt_pl")
            inline.add(item1,item2,item3)
            bot.send_message(message.chat.id, 'Wpisz symbol waluty'.format(message.from_user), reply_markup=inline)

        elif message.text == 'ЦІНА' + '\U0001F4B8':
            inline = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('BITCOIN', callback_data="btc_ua")
            item2 = types.InlineKeyboardButton('ETHEREUM', callback_data="eth_ua")
            item3 = types.InlineKeyboardButton('USDT', callback_data="usdt_ua")
            inline.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Виберіть тікер криптовалюти'.format(message.from_user), reply_markup=inline)

        elif message.text == 'PRICE' + '\U0001F4B8':
            inline = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('BITCOIN', callback_data="btc_uk")
            item2 = types.InlineKeyboardButton('ETHEREUM', callback_data="eth_uk")
            item3 = types.InlineKeyboardButton('USDT', callback_data="usdt_uk")
            inline.add(item1, item2, item3)

            bot.send_message(message.chat.id, 'Enter the cryptocurrency ticker'.format(message.from_user), reply_markup=inline)



        #Пул Have Have UA  Have PL
        elif message.text == 'ПУЛ' + '\U0001F50C':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Hiveon' + '\U0001F1FA'+'\U0001F1E6')
            item2 = types.KeyboardButton('Binance' + '\U0001F1FA'+'\U0001F1E6')
            item3 = types.KeyboardButton('2miners' + '\U0001F1FA'+'\U0001F1E6')
            back = types.KeyboardButton('ВИБІР РОЗДІЛУ')
            markup.add(item1, item2, item3, back)


            bot.send_message(message.chat.id, 'Майнинг-пул (mining pool) – это сервер, который разделяет большую и сложную задачу по вычислению подписи блока на более мелкие и простые задачки и раздаёт их подключённым устройствам. Соответственно, вычислительные мощности участников пула объединяются для решения этой большой задачи, что существенно повышает шансы на нахождение блока.'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Топ майнинг-пулов:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Вибери розділ'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id,'1. Hiveon'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '2. Binance'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '3. 2miners'.format(message.from_user), reply_markup=markup)

        elif message.text == 'Hiveon' + '\U0001F1FA'+'\U0001F1E6':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('ВИБІР РОЗДІЛУ')

            markup.add(back)

            bot.send_message(message.chat.id, 'Обзор пула:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Как начать майнить на пуле Hiveon](https://hiveon.com/ru/knowledge-base/hiveon-pool/)', parse_mode='Markdown')

        elif message.text == 'Binance' + '\U0001F1FA'+'\U0001F1E6':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('ВИБІР РОЗДІЛУ')

            markup.add(back)

            bot.send_message(message.chat.id, 'Обзор пула:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Как начать майнить на пуле Hiveon](https://binanceinfo.ru/binans-pul-dlya-majninga-obzor-i-nastrojka/)', parse_mode='Markdown')

        elif message.text == '2miners' + '\U0001F1FA'+'\U0001F1E6':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('ВИБІР РОЗДІЛУ')

            markup.add(back)

            bot.send_message(message.chat.id, 'Обзор пула:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Как начать майнить на пуле 2miners](https://eth.2miners.com/ru/help)', parse_mode='Markdown')

        #PL
        elif message.text == 'POOL' + '\U0001F50C':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Hiveon' + '\U0001F1F5'+'\U0001F1F1')
            item2 = types.KeyboardButton('Binance' + '\U0001F1F5'+'\U0001F1F1')
            item3 = types.KeyboardButton('2miners' + '\U0001F1F5'+'\U0001F1F1')
            back = types.KeyboardButton('DO WYBORU SEKCJI')
            markup.add(item1, item2, item3, back)


            bot.send_message(message.chat.id, 'Mining pool (mining pool) to serwer, który dzieli duże i złożone zadanie obliczania podpisu bloku na mniejsze i prostsze zadania i rozdaje je podłączonym urządzeniom. W związku z tym moc obliczeniowa uczestników puli jest łączona w celu rozwiązania tego dużego zadania, co znacznie zwiększa szanse na znalezienie bloku.'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Top pule:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Wybierz sekcję'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id,'1. Hiveon'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '2. Binance'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '3. 2miners'.format(message.from_user), reply_markup=markup)

        elif message.text == 'Hiveon' + '\U0001F1F5'+'\U0001F1F1':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('DO WYBORU SEKCJI')

            markup.add(back)

            bot.send_message(message.chat.id, 'Przegląd puli:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Jak rozpocząć wydobycie na puli Hiveon](https://hiveon.com/knowledge-base/hiveon-pool/hiveon-setting-up/)', parse_mode='Markdown')

        elif message.text == 'Binance' + '\U0001F1F5'+'\U0001F1F1':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('DO WYBORU SEKCJI')

            markup.add(back)

            bot.send_message(message.chat.id, 'Przegląd puli:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Jak rozpocząć wydobycie na puli Binance](https://cryps.pl/poradnik/binance-mining-pool/)', parse_mode='Markdown')

        elif message.text == '2miners' + '\U0001F1F5'+'\U0001F1F1':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('DO WYBORU SEKCJI')

            markup.add(back)

            bot.send_message(message.chat.id, 'Przegląd puli:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[Jak rozpocząć wydobycie na puli 2miners](https://eth.2miners.com/pl/help)', parse_mode='Markdown')

        #UK
        elif message.text == 'POOLING' + '\U0001F50C':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Hiveon' + '\U0001F1EC'+'\U0001F1E7')
            item2 = types.KeyboardButton('Binance' + '\U0001F1EC'+'\U0001F1E7')
            item3 = types.KeyboardButton('2miners' + '\U0001F1EC'+'\U0001F1E7')
            back = types.KeyboardButton('SELECTING A SECTION')
            markup.add(item1, item2, item3, back)


            bot.send_message(message.chat.id, 'A mining pool is a server that divides a large and complex task of calculating a block signature into smaller and simpler tasks and distributes them to connected devices. Accordingly, the computing power of the pool participants is combined to solve this large task, which significantly increases the chances of finding a block.'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Top mining pools:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, 'Select a section'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '1. Hiveon'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '2. Binance'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '3. 2miners'.format(message.from_user), reply_markup=markup)

        elif message.text == 'Hiveon' + '\U0001F1EC'+'\U0001F1E7':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('SELECTING A SECTION')

            markup.add(back)

            bot.send_message(message.chat.id, 'Pool Overview:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[How to start mining on the pool Hiveon](https://hiveon.com/knowledge-base/hiveon-pool/hiveon-setting-up/)', parse_mode='Markdown')

        elif message.text == 'Binance' + '\U0001F1EC'+'\U0001F1E7':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('SELECTING A SECTION')

            markup.add(back)

            bot.send_message(message.chat.id, 'Pool Overview:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[How to start mining on the pool Binance](https://mining-cryptocurrency.ru/luchshie-puly-dlya-majninga/)', parse_mode='Markdown')

        elif message.text == '2miners' + '\U0001F1EC'+'\U0001F1E7':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('SELECTING A SECTION')

            markup.add(back)

            bot.send_message(message.chat.id, 'Pool Overview:'.format(message.from_user), reply_markup=markup)
            bot.send_message(message.chat.id, '[How to start mining on the pool 2miners](https://eth.2miners.com/pl/help)', parse_mode='Markdown')

        # Новости
        elif message.text == 'NEWS' + '\U0001F5DE':
            try:
                key = str(message.chat.id)
                bot.send_message(key, "Please wait, we are looking for news")
                uk_articles = NewsParser.get_articles('uk', users[key][1])
                data, max_time = NewsParser.news_parse(users[key], uk_articles, None, None)
                users[key][1] = max_time
                if data == [] or data == None or data == "None":
                    bot.send_message(key, "This is the most up-to-date information for the current time", parse_mode="Markdown")
                for text in data:
                    bot.send_message(key, text, parse_mode="Markdown")
            except KeyError:
                bot.send_message(key, "Sorry we couldn't find you in the database, please write /star ")

        elif message.text == 'WIADOMOŚCI' + '\U0001F5DE':
            try:
                key = str(message.chat.id)
                bot.send_message(key, "Proszę czekać, szukając wiadomości")
                pl_articles = NewsParser.get_articles('pl', users[key][1])
                data, max_time = NewsParser.news_parse(users[key], None, None, pl_articles)
                users[key][1] = max_time
                if data == [] or data == None or data == "None":
                    bot.send_message(key, "Są to najbardziej aktualne informacje na bieżący czas", parse_mode="Markdown")
                for text in data:
                    bot.send_message(key, text, parse_mode="Markdown")
            except KeyError:
                bot.send_message(key, "Przepraszamy nie mogliśmy cię znaleźć w bazie, napisz /start ")

        elif message.text == 'НОВИНИ' + '\U0001F5DE':
            try:
                key = str(message.chat.id)
                bot.send_message(key, "Будь ласка почекайте, шукаємо новини")
                ua_articles = NewsParser.get_articles('ua', users[key][1])
                data, max_time = NewsParser.news_parse(users[key], None, ua_articles, None)
                users[key][1] = max_time
                if data == [] or data == None:
                    bot.send_message(key, "Це найактуальніша інформація на поточний час", parse_mode="Markdown")
                for text in data:
                    bot.send_message(key, text, parse_mode="Markdown")
            except KeyError:
                bot.send_message(key, "Вибачте ми не змогли знайти вас в базі даних, будь ласка напиши /start ")

if __name__ == "__main__":
    try:
        with open("users.json") as json_file:
            # загрузка хеш-таблицы с данными о пользователях бота из файла(В случае если файл пустой создаётся пустая хеш табоица)
            try:
                users = json.load(json_file)
            except TypeError:
                users = {}
        #запуск потока с парсером новостей
        _thread.start_new_thread(send_news, ())
        #запуск потока с ботом
        bot.polling(none_stop=True)
    except Exception as e:
        print(repr(e))
        for key in users.keys():
            bot.send_message(key, "Sorry there was an error on the server side. We are doing everything possible to eliminate it. \n We apologize for the inconvenience")
    finally:
        #в случае ошибки или завершения работы скрипта запускается данный блок кода, в нём данные о пользователях сохраняются в файл
        with open("users.json", "w") as file:
            file.write(json.dumps(users))
