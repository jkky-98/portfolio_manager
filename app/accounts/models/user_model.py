import uuid
from app.libs import db_connection


def add_user(user_name, user_password):
    conn = db_connection.Database().conn
    cursor = conn.cursor()

    sql = """
                 INSERT INTO user_info (id, user_name, user_password)
                 VALUES (%s, %s, SHA2(%s, 256))
              """

    user_id = uuid.uuid4().bytes

    val = (user_id, user_name, user_password)
    cursor.execute(sql, val)
    conn.commit()


def get_user_name(user_name):
    conn = db_connection.Database().conn
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT user_name FROM user_info WHERE user_name=%s"

    val = (user_name,)
    cursor.execute(sql, val)
    row = cursor.fetchall()
    return row[0]['user_name'] if row else None


def get_user(user_name, user_password):
    conn = db_connection.Database().conn
    cursor = conn.cursor(dictionary=True)

    sql = """
                 SELECT user_name, id
                 FROM user_info WHERE user_name=%s AND user_password=SHA2(%s, 256)
              """
    val = (user_name, user_password)
    cursor.execute(sql, val)
    row = cursor.fetchall()

    # return User() class object
    # usage : User.user_name, User.user_id...
    return User.from_row(row[0]) if row else None


class User(object):
    def __init__(self, user_name, user_id):
        self.user_name = user_name
        self.user_id = user_id

    @staticmethod
    def from_request(handler):
        if handler.get_secure_cookie("user"):
            return User(
                handler.get_secure_cookie("user"),
                handler.get_secure_cookie("user_id")
            )

    @staticmethod
    def from_row(row):
        return User(
            row['user_name'],
            str(uuid.UUID(bytes=bytes(row['id'])))
        )


class UserConnectionInfo(object):
    """
    Used in WSHandler for sending user connection information to ThreadAgentsManager thread
    self.ws_connection : if True, it means the WSHandler has invoked add_connection()
                         if False, it means the WSHandler has invoked remove_connection()
    self.client : a current client connected to the websocket server
    self.stock_codes : a current client's stock codes
    self.loop : main IOloop
    """
    def __init__(self, ws_connection, client, stock_codes, loop):
        self.ws_connection = ws_connection
        self.client = client
        self.stock_codes = stock_codes
        self.loop = loop
