class TestTradeHistoryFormats(object):
    """
    To test right and wrong data formats for stock trade history
    It is used in test_handlers.py
    """

    def __init__(self):
        self.trade_history = {'stock_code': 'AAPL',
                              'open_date': '2020-11-22',
                              'trade_type': 'BUY',
                              'open_price': '3000',
                              'amount': '2',
                              'commission': ''}

        self.wrong_stock_code = {'stock_code': 'wrong_stock_code',
                                 'open_date': '2020-11-22',
                                 'trade_type': 'BUY',
                                 'open_price': '3000',
                                 'amount': '2',
                                 'commission': ''}

        self.wrong_trade_type = {'stock_code': 'AAPL',
                                 'open_date': '2020-11-22',
                                 'trade_type': 'WRONG_TYPE',
                                 'open_price': '3000',
                                 'amount': '2',
                                 'commission': ''}

        self.wrong_open_date = {'stock_code': 'AAPL',
                                'open_date': 'WRONG_DATE',
                                'trade_type': 'BUY',
                                'open_price': '3000',
                                'amount': '2',
                                'commission': ''}

        self.wrong_open_price = {'stock_code': 'AAPL',
                                 'open_date': '2020-11-22',
                                 'trade_type': 'BUY',
                                 'open_price': 'WRONG_PRICE',
                                 'amount': '2',
                                 'commission': ''}

        self.wrong_amount = {'stock_code': 'AAPL',
                             'open_date': '2020-11-22',
                             'trade_type': 'BUY',
                             'open_price': '3000',
                             'amount': 'WRONG_AMOUNT',
                             'commission': ''}

        self.wrong_commission = {'stock_code': 'AAPL',
                                 'open_date': '2020-11-22',
                                 'trade_type': 'BUY',
                                 'open_price': '3000',
                                 'amount': '2',
                                 'commission': 'WRONG'}

        # stock_trade_history without stock_code for test_ajax_stock_price()
        self.trade_history_without_stock_code = {'open_date': '2020-11-22',
                                                 'trade_type': 'BUY',
                                                 'open_price': '3000',
                                                 'amount': '2',
                                                 'commission': ''}


class TestUserFormats(object):
    def __init__(self):
        self.test_user = {'user_name': 'test', 'user_password': 'test'}
        self.test_empty_user_name = {'user_name': '', 'user_password': 'test'}
        self.test_empty_user_password = {'user_name': 'test', 'user_password': ''}
