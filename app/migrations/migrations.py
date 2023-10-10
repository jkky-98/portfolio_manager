from app.libs import db_connection

# input 0 to create table "test_table" with columns "test_id", "test_data"
MIGRATION_HEAD = int(input())

db = db_connection.Database()


def create_test_table():
    query = "CREATE TABLE test_table (test_id INT AUTO_INCREMENT PRIMARY KEY, test_data VARCHAR(255))"
    cursor = db.conn.cursor()
    cursor.execute(query)
    db.conn.commit()


def drop_test_table():
    query = "DROP TABLE test_table"
    cursor = db.conn.cursor()
    cursor.execute(query)
    db.conn.commit()


def create_user_info():
    query = """
            CREATE TABLE user_info  (id BINARY(16) PRIMARY KEY,
                                    user_name VARCHAR(255) NOT NULL, 
                                    user_password VARCHAR(255) NOT NULL
                                    ) ENGINE=InnoDB DEFAULT CHARSET=UTF8
            """

    cursor = db.conn.cursor()
    cursor.execute(query)
    db.conn.commit()


def create_stock_trade():
    query = """
            CREATE TABLE stock_trade(id BINARY(16) PRIMARY KEY,
                                    ticker_symbol VARCHAR(255),
                                    open_date DATE,
                                    trade_type VARCHAR(10),
                                    amount FLOAT,
                                    open_price FLOAT,
                                    commission FLOAT,
                                    fk_user_info_stock_trade BINARY(16),
                                    FOREIGN KEY (fk_user_info_stock_trade) REFERENCES user_info(id)
                                    ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=UTF8
            """

    cursor = db.conn.cursor()
    cursor.execute(query)
    db.conn.commit()


MIGRATIONS = [
    create_test_table,
    drop_test_table,
    create_user_info,
    create_stock_trade
]


def run_migration():
    for migration in MIGRATIONS[MIGRATION_HEAD:]:
        migration()


run_migration()
