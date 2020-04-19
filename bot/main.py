import os

from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte

from bot.settings import SHUF_SETTINGS


def main():
    app = Kutana()

    backend = Vkontakte(SHUF_SETTINGS['TOKEN'])
    app.add_backend(backend)
    app.config['prefixes'] = ("test ", "тест ")  #('шаф', 'sb', 'шб', 'shuf', 'shufbot')
    app.config['settings'] = SHUF_SETTINGS

    app.add_plugins(load_plugins(os.path.join(os.curdir, 'bot', 'plugins')))

    return app
