import tornado.web
import tornado.escape
import tornado.websocket
import tornado.locks
import tornado.ioloop
import json
import urllib.parse
import settings

from tornado.concurrent import run_on_executor
from tornado.gen import multi

from app.accounts.models.user_model import UserConnectionInfo
from app.stock.controller import stock_price_controller
from app.stock.models import stock_trade_model
from app.accounts.handlers.login_handler import BaseHandler
from app.utils.logger import logger
from app.utils.util import current_date
from app.utils.handle_errors import check_data
from app.utils.config_parser import get_frontend_config


# to get data input by html form and transmit input data into MySQL server to save it
class DataInsertHandler(BaseHandler):
    def __init__(self, application, request):
        super(DataInsertHandler, self).__init__(application, request)
        self.stock_code_model = stock_trade_model.StockTrade()
        self.user_id = tornado.escape.xhtml_escape(self.current_user.user_id)

    def post(self):
        self.set_header("Content-Type", "text/plain")

        stock_trade_data = tornado.escape.json_decode(self.request.body)

        stock_code = stock_trade_data.get('stock_code', '').upper()
        open_date = stock_trade_data.get('open_date', '') or current_date()
        trade_type = stock_trade_data.get('trade_type', '').upper()
        open_price = stock_trade_data.get('open_price', '')
        amount = stock_trade_data.get('amount', '')
        commission = stock_trade_data.get('commission', '') or 0

        success, message = check_data(
            open_date,
            trade_type,
            open_price,
            amount,
            commission,
            stock_code
        )
        if not success:
            data_info_json = {'success': False, 'error_msg': message}
            self.write(data_info_json)
            return self.set_status(500, "Data Error")

        # if input stock data is not available, it shows error message
        current_price = stock_price_controller.get_current_price(stock_code)

        # if current_price is successfully received without errors, it returns float type
        # otherwise, it returns (status=False, error_msg)
        if isinstance(current_price, tuple):
            status, error_msg = current_price
            if not status:
                data_info_json = {'success': False, 'error_msg': error_msg}
                self.write(data_info_json)
                return self.set_status(500, "Data Error")

        add_stock_trade = self.stock_code_model.add_stock_trade(self.user_id,
                                                                stock_code,
                                                                open_date,
                                                                trade_type,
                                                                amount,
                                                                open_price,
                                                                commission
                                                                )
        if add_stock_trade is None:
            logger.debug('Data-type or Data-Value Error in "self.user_id"')

            data_info_json = {'success': False, 'error_msg': 'Data-type or Data-Value Error'}
            self.write(json.dumps(data_info_json))
            return self.set_status(500, "Data Error")

        data_info_json = {'success': True, 'error_msg': ''}
        self.write(json.dumps(data_info_json))


class WSHandler(tornado.websocket.WebSocketHandler, BaseHandler):
    def __init__(self, application, request, queue):
        super(WSHandler, self).__init__(application, request)
        self.user_id = tornado.escape.xhtml_escape(self.current_user.user_id)
        self.stock_code_model = stock_trade_model.StockTrade()

        stock_trade_history = self.stock_code_model.get_stock_trade(self.user_id)
        self.stock_codes = list(stock_trade_history.keys())

        self.loop = tornado.ioloop.IOLoop.current()
        self.queue = queue

    def add_connection(self):
        user_conn_info = UserConnectionInfo(True, self, self.stock_codes, self.loop)
        self.queue.put(user_conn_info)

    def remove_connection(self):
        user_conn_info = UserConnectionInfo(False, self, self.stock_codes, None)
        self.queue.put(user_conn_info)

    def open(self):
        logger.info("Websocket Connection Opened")
        self.add_connection()

    def on_close(self):
        logger.info("Websocket Connection Closed")
        self.remove_connection()

    def check_origin(self, origin):
        parsed_origin = urllib.parse.urlparse(origin)
        return parsed_origin.netloc.endswith(get_frontend_config('frontend_server_url_host'))


class AjaxStockPriceHandler(BaseHandler):
    def __init__(self, application, request, executor):
        super(AjaxStockPriceHandler, self).__init__(application, request)
        self.stock_code_model = stock_trade_model.StockTrade()
        self.user_id = tornado.escape.xhtml_escape(self.current_user.user_id)
        self.executor = executor

    # get current stock price asynchronously
    # The executor to be used is determined by the executor attributes of self (self.executor)
    @run_on_executor(executor='executor')
    def get_stock_price(self, stock_code):
        current_price = stock_price_controller.get_current_price(stock_code)
        return current_price

    @tornado.web.authenticated
    async def get(self):
        stock_trade_history = self.stock_code_model.get_stock_trade(self.user_id)

        if stock_trade_history is None:
            logger.debug('Data-type or Data-Value Error in "self.user_id"')

            stock_trade_info_json = {'success': False, 'error_msg': 'Data-type or Data-Value Error'}
            self.write(json.dumps(stock_trade_info_json))
            return self.set_status(500, "Data Error")
        elif stock_trade_history == dict():
            stock_trade_info_json = {'success': False, 'error_msg': 'No Data'}
            self.write(json.dumps(stock_trade_info_json))
            return self.set_status(500, "Data Error")

        stock_codes = stock_trade_history.keys()

        # run get_current_price async threads and wait for future objects until they are loaded
        current_stock_price_dict = await multi(
            {stock_code: self.get_stock_price(stock_code) for stock_code in stock_codes})

        for stock_code in stock_codes:
            current_price = current_stock_price_dict[stock_code]
            stock_trade_history[stock_code]["current_price"] = current_price

        return self.write(json.dumps(stock_trade_history))
