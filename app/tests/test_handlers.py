import sys
import asyncio
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.websocket
import json
import uuid
import queue

from app.stock.handlers.stock_handlers import DataInsertHandler, AjaxStockPriceHandler, WSHandler
from app.accounts.handlers.signup_handler import SignUpHandler
from app.accounts.handlers.login_handler import LoginHandler, LogoutHandler
from app.accounts.models.user_model import User
from app.tests.test_formats import TestTradeHistoryFormats, TestUserFormats
from app.utils.config_parser import (
                                    read_config, get_backend_config,
                                    get_db_config, get_frontend_config
                                )

from tornado.testing import AsyncHTTPTestCase
from unittest.mock import patch
from tornado import gen
from concurrent.futures import ThreadPoolExecutor


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class TestHandlers(AsyncHTTPTestCase):
    def setUp(self):
        self.test_user_id = str(uuid.uuid4())
        self.test_user_formats = TestUserFormats()
        self.test_user = self.test_user_formats.test_user
        self.test_empty_user_name = self.test_user_formats.test_empty_user_name
        self.test_empty_user_password = self.test_user_formats.test_empty_user_password
        AsyncHTTPTestCase.setUp(self)

    # TODO
    def tearDown(self):
        pass

    def get_app(self):
        return make_app()

    @patch('app.accounts.models.user_model.get_user_name')
    @patch('app.libs.db_connection.Database')
    def test_sign_up(self, mock_database, mock_user_name):
        mock_user_name.return_value = None

        test_formats = [self.test_user, self.test_empty_user_name, self.test_empty_user_password]

        # to test success with test user, and failure with empty user_name or user_password
        for test_format in test_formats:
            response = self.fetch('/sign-up', method='POST', body=json.dumps(test_format))
            sign_up_info_json = tornado.escape.json_decode(response.body)
            success = sign_up_info_json['success']
            error_msg = sign_up_info_json['error_msg']

            if test_format is self.test_user:
                self.assertEqual(success, True)
                self.assertEqual(error_msg, '')
            else:
                self.assertEqual(success, False)
                self.assertEqual(error_msg, 'empty user name or password')

        # to test already existing user_name
        mock_user_name.return_value = 'test'

        response = self.fetch('/sign-up', method='POST', body=json.dumps(self.test_user))
        sign_up_info_json = tornado.escape.json_decode(response.body)

        success = sign_up_info_json['success']
        error_msg = sign_up_info_json['error_msg']

        self.assertEqual(success, False)
        self.assertEqual(error_msg, 'already existing user name')

    def test_login(self):
        # login success test, failure tests(without username, password)
        test_formats = [self.test_user, self.test_empty_user_name, self.test_empty_user_password]

        for test_format in test_formats:
            response = self.fetch('/login', method='POST', body=json.dumps(test_format))
            login_info_json = tornado.escape.json_decode(response.body)
            success = login_info_json['success']
            current_user_name = login_info_json['current_user_name']
            error_msg = login_info_json['error_msg']

            if success:
                self.assertEqual(success, True)
                self.assertEqual(current_user_name, 'test')
                self.assertEqual(error_msg, '')
                self.assertEqual(response.code, 200)
            else:
                self.assertEqual(success, False)
                self.assertEqual(current_user_name, '')
                self.assertEqual(error_msg, 'Wrong ID or Password')
                self.assertEqual(response.code, 200)

    def test_logout(self):
        response = self.fetch('/logout')
        logout_info_json = tornado.escape.json_decode(response.body)
        success = logout_info_json['success']
        error_msg = logout_info_json['error_msg']

        self.assertEqual(success, True)
        self.assertEqual(error_msg, '')

    @patch('app.accounts.handlers.login_handler.BaseHandler.get_current_user')
    @patch('app.libs.db_connection.Database')
    def test_input_stock_code(self, mock_database, mock_current_user):
        mock_current_user.return_value = User('test', self.test_user_id)

        test_formats = TestTradeHistoryFormats()

        trade_history = test_formats.trade_history

        wrong_stock_code = test_formats.wrong_stock_code
        wrong_trade_type = test_formats.wrong_trade_type
        wrong_open_date = test_formats.wrong_open_date
        wrong_open_price = test_formats.wrong_open_price
        wrong_amount = test_formats.wrong_amount
        wrong_commission = test_formats.wrong_commission

        test_formats = [trade_history,
                        wrong_stock_code,
                        wrong_trade_type,
                        wrong_open_date,
                        wrong_open_price,
                        wrong_amount,
                        wrong_commission]

        for test_format in test_formats:
            response = self.fetch('/input-stock-code', method='POST', body=json.dumps(test_format))
            stock_trade_info_json = tornado.escape.json_decode(response.body)

            success = stock_trade_info_json['success']
            error_msg = stock_trade_info_json['error_msg']

            if test_format is trade_history:
                self.assertEqual(success, True)
            else:
                self.assertEqual(success, False)

            if test_format is trade_history:
                self.assertEqual(error_msg, '')
            elif test_format is wrong_stock_code:
                self.assertEqual(error_msg, 'stock data was not found')
            elif test_format is wrong_trade_type:
                self.assertEqual(error_msg, "trade type should be either 'BUY' or 'SELL'")
            else:
                self.assertEqual(error_msg, "wrong format data")

    @patch('app.stock.models.stock_trade_model.StockTrade.get_stock_trade')
    @patch('app.accounts.handlers.login_handler.BaseHandler.get_current_user')
    def test_ajax_stock_price(self, mock_current_user, mock_stock_trade):
        mock_current_user.return_value = User('test', self.test_user_id)

        trade_history_without_stock_code = TestTradeHistoryFormats().trade_history_without_stock_code
        trade_history = {'AAPL': {'trade_history': {'test_trade_id': trade_history_without_stock_code}},
                         'MSFT': {'trade_history': {'test_trade_id': trade_history_without_stock_code}}}

        mock_stock_trade.return_value = trade_history

        response = self.fetch('/show-all')
        stock_trade_history_json = tornado.escape.json_decode(response.body)
        aapl_current_price = stock_trade_history_json['AAPL'].get('current_price', None)
        msft_current_price = stock_trade_history_json['MSFT'].get('current_price', None)

        self.assertEqual(isinstance(aapl_current_price, float), True)
        self.assertEqual(isinstance(msft_current_price, float), True)

        # test the case of trade history being empty dict()
        empty_trade_history = dict()

        mock_stock_trade.return_value = empty_trade_history
        response = self.fetch('/show-all')
        stock_trade_info_json = tornado.escape.json_decode(response.body)
        success = stock_trade_info_json['success']
        error_msg = stock_trade_info_json['error_msg']

        self.assertEqual(success, False)
        self.assertEqual(error_msg, 'No Data')

        # test the case of trade history being None
        none_trade_history = None

        mock_stock_trade.return_value = none_trade_history
        response = self.fetch('/show-all')
        stock_trade_info_json = tornado.escape.json_decode(response.body)
        success = stock_trade_info_json['success']
        error_msg = stock_trade_info_json['error_msg']

        self.assertEqual(success, False)
        self.assertEqual(error_msg, 'Data-type or Data-Value Error')

    @patch('app.stock.handlers.stock_handlers.WSHandler.remove_connection')
    @patch('app.stock.handlers.stock_handlers.WSHandler.add_connection')
    @patch('app.stock.models.stock_trade_model.StockTrade.get_stock_trade')
    @patch('app.accounts.handlers.login_handler.BaseHandler.get_current_user')
    @tornado.testing.gen_test
    def test_websocket(self, mock_current_user, mock_stock_trade, mock_add_connection, mock_remove_connection):
        mock_current_user.return_value = User('test', self.test_user_id)

        trade_history_without_stock_code = TestTradeHistoryFormats().trade_history_without_stock_code
        trade_history = {'AAPL': {'trade_history': {'test_trade_id': trade_history_without_stock_code}},
                         'MSFT': {'trade_history': {'test_trade_id': trade_history_without_stock_code}}}

        mock_stock_trade.return_value = trade_history

        ws_url = "ws://localhost:" + str(self.get_http_port()) + "/ws"

        ws = yield tornado.websocket.websocket_connect(ws_url)
        ws.close()
        # to wait enough time for remove_connection in on_close() to be invoked
        yield tornado.gen.sleep(1)
        # check if the client has invoked add_connection in open()
        mock_add_connection.assert_called_once()
        # check if the client has invoked on_close() in on_close()
        mock_remove_connection.assert_called_once()

    def test_config_parser(self):
        read_config('app/tests/test_config.ini')

        database = get_db_config('database')
        port = get_backend_config('port')
        frontend_server_url_host = get_frontend_config('frontend_server_url_host')

        self.assertEqual(database, 'PortfolioManager')
        self.assertEqual(port, '8888')
        self.assertEqual(frontend_server_url_host, 'localhost:8080')


def make_app():
    executor = ThreadPoolExecutor(max_workers=4)
    thread_agent_manager_queue = queue.Queue()

    settings = {
        "cookie_secret": "0123456789",
        "login_url": "/login"
    }

    try:
        read_config('app/tests/test_config.ini')
    except FileNotFoundError:
        sys.exit()
    
    return tornado.web.Application([
        (r"/login", LoginHandler),
        (r"/input-stock-code", DataInsertHandler),
        (r"/show-all", AjaxStockPriceHandler, dict(executor=executor)),
        (r"/logout", LogoutHandler),
        (r"/sign-up", SignUpHandler),
        (r"/ws", WSHandler, dict(queue=thread_agent_manager_queue)),
    ], **settings)


if __name__ == '__main__':
    import unittest

    unittest.main()
