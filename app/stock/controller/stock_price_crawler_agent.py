import threading
import json
import time
import functools

from app.stock.controller.stock_price_controller import get_current_price
from app.utils.logger import logger


SUICIDE_TIME = 5
PRICE_PUSH_CYCLE = 5


class ThreadAgentsManager(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.stock_agents = dict()
        self.queue = queue
        self.stopped = threading.Event()
        self.clients_lock = threading.Lock()

    def add_stock_price_agent(self, client, stock_codes, loop):
        for stock_code in stock_codes:
            agent = self.stock_agents.get(stock_code, None)
            # to avoid re-making already existing thread
            # if the agent thread is dead, it substitutes the dead one with a new agent thread instance
            if agent is None or not agent.is_alive():
                agent = StockPriceCrawlerAgent(stock_code, loop, self.stopped, self.clients_lock)
                agent.start()
                self.stock_agents[stock_code] = agent
            agent.add_client(client)

    # it removes a corresponding client when connected websocket server dies
    def remove_stock_price_agent(self, client, stock_codes):
        for stock_code in stock_codes:
            self.stock_agents[stock_code].remove_client(client)

    def stop(self):
        self.stopped.set()

    def run(self):
        while not self.stopped.is_set():
            user_conn_info = self.queue.get()

            if user_conn_info.ws_connection:
                self.add_stock_price_agent(user_conn_info.client, user_conn_info.stock_codes, user_conn_info.loop)
            else:
                self.remove_stock_price_agent(user_conn_info.client, user_conn_info.stock_codes)


class StockPriceCrawlerAgent(threading.Thread):
    """
    a thread which pushes stock prices to corresponding clients
    one StockPriceCrawlerAgent object code is created per one stock code
    if there is no clients for more than suicide time, the thread breaks
    """
    def __init__(self, stock_code, loop, stopped, clients_lock):
        super().__init__(name=stock_code)
        self.clients = list()
        self.stock_code = stock_code
        self.stopped = stopped
        self.loop = loop
        self.clients_lock = clients_lock

        self.suicide_time = None

    def add_client(self, client):
        with self.clients_lock:
            self.clients.append(client)

    # removes client
    # if there is no client left, it sets suicide time for the StockPriceCrawlerAgent thread object
    def remove_client(self, client):
        with self.clients_lock:
            self.clients.remove(client)

        if self.is_empty():
            self.set_suicide_time()

    def set_suicide_time(self):
        self.suicide_time = time.time()

    # check if there is no existing client
    def is_empty(self):
        with self.clients_lock:
            return len(self.clients) == 0

    def run(self):
        while not self.stopped.is_set():
            # if there is no client for more than suicide time(currently 5sec), it kills the thread
            if self.suicide_time:
                if not self.is_empty():
                    self.suicide_time = None
                else:
                    if time.time() > self.suicide_time + SUICIDE_TIME:
                        # TODO : delete self.stock_agents[self.stock_code] using Garbage Collector if it is dead
                        break

            stock_price = get_current_price(self.stock_code)
            with self.clients_lock:
                for client in self.clients:
                    data = json.dumps({self.stock_code: stock_price})

                    # write_message method in WSHandler can be only used in main thread
                    # add_callback method can make it possible
                    # partial func fixes binding issue with local variable 'client' in for loop
                    def callback(client):
                        client.write_message(data)
                    self.loop.add_callback(functools.partial(callback, client))

            # push current stock price every 5 seconds
            if not self.is_empty():
                time.sleep(PRICE_PUSH_CYCLE)
        logger.info("Breaking Thread : {}".format(self))
