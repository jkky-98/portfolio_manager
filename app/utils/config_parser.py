from configparser import ConfigParser


def read_config(file_path):
    parser = ConfigParser()
    parser.read(file_path)

    global app_config
    app_config = parser


def _get_config(config_section):
    return app_config[config_section]


def get_db_config(config_name):
    return _get_config('database')[config_name]


def get_backend_config(config_name):
    return _get_config('backend')[config_name]


def get_frontend_config(config_name):
    return _get_config('frontend')[config_name]
