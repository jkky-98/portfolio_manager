import uuid
from app.libs import db_connection
from app.utils.logger import logger


class StockTrade(object):
    def __init__(self):
        self.conn = db_connection.Database().conn

    def add_stock_trade(self, fk, stock_code, open_date, trade_type, amount, open_price, commission):
        cursor = self.conn.cursor()
        sql = """INSERT INTO stock_trade 
                 (id, ticker_symbol, open_date, trade_type, amount, open_price, commission, fk_user_info_stock_trade)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                 """

        stock_trade_id = uuid.uuid4().bytes
        try:
            val = (
                stock_trade_id, stock_code, open_date, trade_type, amount, open_price, commission, uuid.UUID(fk).bytes)
        except Exception:
            logger.exception("add_stock_trade() error")
            return None

        cursor.execute(sql, val)
        self.conn.commit()
        return True

    def get_stock_trade(self, fk):
        cursor = self.conn.cursor()
        sql = """
                 SELECT ticker_symbol, id, open_date, trade_type, amount, open_price, commission 
                 FROM stock_trade
                 WHERE fk_user_info_stock_trade = %s
              """

        try:
            val = (uuid.UUID(fk).bytes,)
        except Exception:
            logger.exception("add_stock_trade() error : ")
            return None

        cursor.execute(sql, val)
        row = cursor.fetchall()

        trade_dict = dict()
        for stock_code, trade_id, *trade_history in row:
            trade_history[0] = trade_history[0].strftime('%Y-%m-%d')

            # register additional trade_history with different trade_id for the same stock_code
            trade_dict.setdefault(stock_code, {}).setdefault("trade_history", {})[
                str(uuid.UUID(bytes=bytes(trade_id)))] = trade_history
        return trade_dict
