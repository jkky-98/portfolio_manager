import datetime
from enum import Enum


class TradeType(Enum):
    BUY = 'buy'
    SELL = 'sell'


def current_time():
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    return time_now


def current_date():
    date_now = datetime.datetime.now().strftime('%Y-%m-%d')
    return date_now
