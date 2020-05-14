import os
# import logging
from datetime import time

from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte

from bot.db import models, database
from bot.settings import SHUF_SETTINGS


# from kutana.logger import set_logger_level


def init_db(app):
    app.config['database'] = database
    username = app.config['settings']['DB_USER']
    password = app.config['settings']['DB_PASSWORD']
    host = app.config['settings']['DB_HOST']
    db_name = app.config['settings']['DB_NAME']
    app.config['database'].init(db_name, user=username, password=password, host=host)
    app.config['database'].create_tables(models)
    app.config['database'].close()
    app.config['database'].set_allow_sync(False)


def main():
    app = Kutana()
    # set_logger_level(logging.DEBUG)

    backend = Vkontakte(SHUF_SETTINGS['TOKEN'])
    app.add_backend(backend)
    app.config['settings'] = SHUF_SETTINGS
    app.config['chat_prefixes'] = ('еш ', 'есб ', 'esb ', 'ешаф ', 'eshuf ')  # ('шаф ', 'sb ', 'шб ', 'shuf ', 'shufbot ')
    app.config['prefixes'] = ('',)  # clean default settings (monkey patch)
    app.config['inform_time'] = time(20, 50)  # 12:00
    app.config['votekick_time'] = 5 * 60
    app.config['git_branch'] = 'develop'
    init_db(app)

    app.add_plugins(load_plugins(os.path.join(os.curdir, 'bot', 'plugins')))

    return app
