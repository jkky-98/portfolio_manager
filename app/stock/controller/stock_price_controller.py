import investpy
import json
import re

from app.utils.handle_errors import stock_handle_errors
from app.utils.logger import logger
from app.utils.util import current_time


# get parameter (stock ticker symbol), and decide whether the country is south korea or united states
def get_current_price(stock_symbol):
    # south korea ticker symbol starts with a number while that of United states starts with an alphabet
    x = re.match("[0-9]", stock_symbol)

    country = "south korea" if x else "united states"

    try:
        current_price_raw = investpy.stocks.get_stock_recent_data(stock_symbol, country, as_json=True,
                                                                  order='descending', interval='Daily')
    except Exception as e:
        logger.exception("get_current_price() error")
        return stock_handle_errors(e)

    current_price_dict = json.loads(current_price_raw)

    current_price = current_price_dict['recent'][0]['close']
    return current_price
