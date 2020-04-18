import os
import logging

from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte
from kutana.logger import set_logger_level

from bot.settings import SHUF_SETTINGS


def main():
    app = Kutana()
    set_logger_level(logging.DEBUG)

    backend = Vkontakte(SHUF_SETTINGS['TOKEN'])
    app.add_backend(backend)
    app.config['prefixes'] = app.config['prefixes'] + ("test ", "тест ")  #['шаф', 'sb', 'шб', 'shuf', 'shufbot']
    app.config['settings'] = SHUF_SETTINGS

    app.add_plugins(load_plugins(os.path.join(os.curdir, 'bot', 'plugins')))

    return app
