import tornado.httpserver
import tornado.ioloop
import tornado.web
import sys
import asyncio
import settings
import queue
import argparse

from concurrent.futures import ThreadPoolExecutor
from app.stock.handlers.stock_handlers import DataInsertHandler, AjaxStockPriceHandler, WSHandler
from app.accounts.handlers.signup_handler import SignUpHandler
from app.accounts.handlers.login_handler import LoginHandler, LogoutHandler
from app.stock.controller.stock_price_crawler_agent import ThreadAgentsManager

from app.utils.logger import logger
from app.utils.config_parser import read_config, get_backend_config


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # The default has changed from selector to pro-actor in Python 3.8.
    # Thus, this line should be added to detour probable errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='tornado development environment settings')
    parser.add_argument( '--env',
                        type=str,
                        default='dev',
                        choices=['dev', 'prod'],
                        help="select environment between 'dev', 'prod'"
                    )
    args = parser.parse_args()
    env = args.env

    try:
        read_config("config/{env}.ini".format(env=env))
    except FileNotFoundError:
        logger.exception('config environment name "{env}" does not exist'.format(env=env))
        sys.exit()
    
    executor = ThreadPoolExecutor(max_workers=4)
    thread_agent_manager_queue = queue.Queue()

    settings_ = {"template_path": settings.TEMPLATE_PATH,
                "static_path": settings.STATIC_PATH,
                "cookie_secret": get_backend_config('cookie_secret'),
                }

    application = tornado.web.Application([
        (r"/login", LoginHandler),
        (r"/input-stock-code", DataInsertHandler),
        (r"/ws", WSHandler, dict(queue=thread_agent_manager_queue)),
        (r"/show-all", AjaxStockPriceHandler, dict(executor=executor)),
        (r"/logout", LogoutHandler),
        (r"/sign-up", SignUpHandler)
    ], **settings_)

    http_server = tornado.httpserver.HTTPServer(application)

    socket_address = get_backend_config('port')
    http_server.listen(socket_address)

    thread_agent_manager = ThreadAgentsManager(thread_agent_manager_queue)
    thread_agent_manager.start()

    loop = tornado.ioloop.IOLoop.current()
    loop.start()

    thread_agent_manager.stop()
