import os
import sys
import argparse

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def dbmigrate():
    from bot.db import database
    username = os.environ['SHUF_DB_HOST']
    password = os.environ['SHUF_DB_PASSWORD']
    host = os.environ['SHUF_DB_HOST']
    db_name = os.environ['SHUF_DB_NAME']

    database.init(db_name, user=username, password=password, host=host)
    database.evolve()


actions = {
    'dbmigrate': dbmigrate
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=list(actions.keys()), required=True, help='action to do')
    args = parser.parse_args(sys.argv)
    actions[args.action]()


if __name__ == '__main__':
    main()
