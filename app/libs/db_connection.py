import mysql.connector

from app.utils.config_parser import get_db_config


class Database(object):
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=get_db_config('host'),
            password=get_db_config('password'),
            user=get_db_config('user'),
            database=get_db_config('database'),
            use_pure=True,
            auth_plugin='mysql_native_password'
        )
        self.conn.set_charset_collation('utf8', 'utf8_general_ci')
