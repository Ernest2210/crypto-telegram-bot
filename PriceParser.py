#модуль отвечающий за парсинг цен

import requests
from bs4 import BeautifulSoup
from Variables import headers
def get_btc_price():
    url = "https://www.coingecko.com/en/coins/bitcoin"
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return str(soup.find("span", class_="tw-text-gray-900 dark:tw-text-white tw-text-3xl").text[1:])

def get_usdt_price():
    url = "https://www.coingecko.com/en/coins/tether"
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return str(soup.find("span", class_="tw-text-gray-900 dark:tw-text-white tw-text-3xl").text[1:])

def get_eth_price():
    url = "https://www.coingecko.com/en/coins/ethereum"
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return str(soup.find("span", class_="tw-text-gray-900 dark:tw-text-white tw-text-3xl").text[1:])