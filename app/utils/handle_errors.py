import datetime
from app.utils.logger import logger
from app.utils.util import current_time, TradeType


def stock_handle_errors(error):
    error_msg = str()
    status = False

    if type(error) == IOError:
        error_msg = "stocks object/file was not found or unable to retrieve"
    elif type(error) == IndexError:
        error_msg = "stock data input was unavailable or not found in Investing.com"
    elif type(error) == RuntimeError:
        error_msg = "stock data was not found"
    elif type(error) == ValueError:
        error_msg = "you have not registered anything"
    return status, error_msg


def check_data(open_date, trade_type, open_price, amount, commission, stock_code):
    if "" in [trade_type, open_price, amount, stock_code]:
        return False, "input the necessary information"

    if trade_type not in TradeType.__members__:
        return False, "trade type should be either 'BUY' or 'SELL'"

    try:
        datetime.datetime.strptime(open_date, '%Y-%m-%d')
    except Exception:
        logger.exception("{}, wrong format datetime".format(current_time()))
        return False, "wrong format data"

    success, message = check_float(open_price, amount, commission)
    return success, message


def check_float(*args):
    try:
        [float(i) for i in args]
    except Exception:
        logger.exception("{}, wrong input format for float type".format(current_time()))
        return False, "wrong format data"
    return True, ""
