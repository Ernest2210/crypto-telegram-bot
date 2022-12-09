#Модуль с частоиспользуемыми переменными, что бы в случае необходимости легко заменить значение переменной во всех местах

#токен бота
TOKEN = 'TOKEN'
#хеш-таблица с данными о пользователях
users = {}
#частота автоматического парсинга новостей в секндах
parse_delay = 1800
#заголовки Fake-user-agent для requsts запросов
headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }