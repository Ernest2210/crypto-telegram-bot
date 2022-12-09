#Модуль, отвечающий за парсинг новостей
import requests
from bs4 import BeautifulSoup
import json
from Variables import headers

#Данная функция возвращает статьи которые выложили позже определённого времени
# (sended_news по умолчанию = 0 - будут пересланы все найденные новости) на заданном языке(language)
def get_articles(language , sended_news=0):
    global headers
    if language == "ua":
        language = "ru"
    if language == 'uk':
        language = "en"
    #получение страницы со списком новостей на заданном языке
    url = f"https://www.binance.com/{language}/support/announCEmeNT/c-49"
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    #Binance не высылает сразу страницу в html, а подгружает их из js скрипта, поэтому далее происхожит парсинг json объекта
    last_news = str(soup.find("script", id="__APP_DATA"))[48:-9]
    data = json.loads(last_news)
    catalogs = data['routeProps']['b723']['catalogs']
    items = None
    for catalog in catalogs:
        if catalog['catalogId'] == 49:
            items = catalog
            break
    items = items['articles']
    articles = []
    # данный цикл проходит по всем найденным статьям и заходит по их сслкам для парсинга текста
    for item in items:
        post_time = item['releaseDate']
        article = get_text_of_article(f"https://www.binance.com/{language}/support/announCEmeNT/", item['code'], post_time, item['title'])
        #Binance при множественных запросах отправляет бесконечный redirect поэтому статья может не вернуться тут происходит проверка на это
        if article != None:
            #Если данная статья старше той которую уже отправляи пользователю, то значит он уже видел её и остальные => нет смыслв искать дальше(выход из цикла)
            if article[2] <= sended_news:
                break
            #добавление статьи в массив
            articles.append(article)
    return articles

#функция для парсинга текста из статьи в формате [текст статьи, ссылка на статью, время постинга статьи, название статьи]
def get_text_of_article(base_url, key, post_time, name):
    global headers
    try:
        session = requests.Session()
        session.max_redirects = 30
        response = session.get(base_url + key, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('div', class_='css-1mw8ice').find_all("div")
        if article == None:
            article = soup.find('div', class_='css-1kytfqv').find_all("div")
        text_of_article = ""
        if article[0]['class'] == 'css-vkkztj':
            text_of_article += article[1].text + "\n"
            text_of_article += article[2].text
        else:
            text_of_article += article[0].text + "\n"
            text_of_article += article[1].text
        words = text_of_article.split(" ")
        return [" ".join(words[:50]), base_url + key, post_time, name]
    except requests.exceptions.TooManyRedirects:
        return ["", base_url+key, post_time, name]

#основная функция парсинга принимает информацию о пользователе, которому отправляют статью и списки доступнх статей на всех языках
#оканчательно отбирает статьи которые не видел пользователь и возвращает список сообщений и время самой свежей статьи для записи в параметры пользователя в хэш таблице
def news_parse(user, uk_articles, ua_articles, pl_articles):
    max_time = int(user[1])
    data_to_send = []
    if user[0] == 'uk':
        for article in uk_articles:
            if int(article[2]) > int(user[1]):
                if int(article[2]) > max_time:
                    max_time = int(article[2])
                data_to_send.append(f"*{article[3]}* \n\n {article[0]}... \n\n {article[1]}")
    elif user[0] == 'ua':
        for article in ua_articles:
            if int(article[2]) > int(user[1]):
                if int(article[2]) > int(user[1]):
                    if int(article[2]) > max_time:
                        max_time = int(article[2])
                    data_to_send.append(f"*{article[3]}* \n\n {article[0]}... \n\n {article[1]}")
    if user[0] == 'pl':
        for article in pl_articles:
            if int(article[2]) > int(user[1]):
                if int(article[2]) > int(user[1]):
                    if int(article[2]) > max_time:
                        max_time = int(article[2])
                    data_to_send.append(f"*{article[3]}* \n\n {article[0]}... \n\n {article[1]}")
    return data_to_send, max_time
