import telebot
import requests
import json

# Создаем экземпляр бота
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot('5705559366:AAEAmTFZy3DqvTiuZCFdR7yGL_A0KST21vg')

adv_url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "123",
    "content-type": "application/json",
    "Host": "p2p.binance.com",
    "Origin": "https://p2p.binance.com",
    "Pragma": "no-cache",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


def get_request(trade_type, fiat, pay_types):
    data = {
        "asset": "USDT",
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "payTypes": pay_types,
        "publisherType": None,
        "rows": 20,
        "tradeType": trade_type
    }

    r = requests.post(adv_url, headers=headers, json=data)

    if r.status_code == 200:
        return sorted(list(map(lambda x: x['adv'], r.json()['data'])), key=lambda k: k['price'])

    return list()


def delete_none_props(x):
    obj = {}
    for key in x.keys():
        if x[key] is not None:
            obj[key] = x[key]
    return obj


def process_data_none(none_data):
    return list(map(delete_none_props, none_data))


def get_data(trade_type, fiat, pay_types):
    return process_data_none(get_request(trade_type, fiat, pay_types))


fiats = ["RUB", "KZT"]

payments = {
    "RUB": ["TinkoffNew", "RosBankNew", "RaiffeisenBank"],
    "KZT": ['KaspiBank', 'HalykBank', 'JysanBank']
}

symbols = {
    "RUB": '₽',
    "KZT": '₸'
}


def get_median_price(trade_type, fiat, pay_types):
    advs = get_data(trade_type, fiat, pay_types)
    return float(advs[int(len(advs) / 2)]['price'])


def get_roi(fiat):
    buy = get_median_price("BUY", fiat, payments[fiat])
    sell = get_median_price("SELL", fiat, payments[fiat])
    return buy, sell, ((buy / sell) * 100) - 100


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, 'Я на связи. Напиши мне что-нибудь )')


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["roi"])
def calc_roi(m, res=False):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in fiats:
        item = KeyboardButton(button)
        markup.add(item)
    bot.send_message(m.chat.id,
                     'Выберите фиатную валюту для расчета ROI',
                     reply_markup=markup)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text in fiats:
        buy, sell, roi = get_roi(message.text)
        bot.send_message(message.chat.id, f"Для фиата {message.text} ROI составляет {round(roi, 2)}%\n"
                                          f"Медианная цена скупки: {sell}{symbols[message.text]}\n"
                                          f"Медианная цена продажи: {buy}{symbols[message.text]}")
    else:
        bot.send_message(message.chat.id, 'Неверный фиат')


# Запускаем бота
bot.polling(none_stop=True, interval=0)
