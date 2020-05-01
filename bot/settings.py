import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get_group_settings(group_name='shuf'):
    group = {}
    for k, v in os.environ.items():
        if k.startswith(group_name.upper() + '_'):
            group[k[len(group_name) + 1:]] = v
    return group


SHUF_SETTINGS = get_group_settings()
