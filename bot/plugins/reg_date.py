import time
import datetime

from aiohttp import ClientSession

from bot.plugin import CustomPlugin as Plugin
from bot.roles import chat_only
from bot.utils import extract_users

plugin = Plugin('Reg date', 'Выводит дату регистрации пользователя')

session = ClientSession()


async def get_registration_date(user_id):
    async with session.get("https://vk.com/foaf.php", params=dict(id=user_id)) as response:
        text = await response.text()
        date = text[text.find('<ya:created dc:date="') + 21:]
        date = date[:date.find('"')]
        a = time.strptime(date, '%Y-%m-%dT%H:%M:%S+03:00')
        return a


def format_registration_date(reg_datetime):
    """
    :param reg_datetime: a registration datetime structure
    :return: tuple of (user_time, user_date)
    """
    return time.strftime('%H:%M', reg_datetime), time.strftime('%d.%m.%Y', reg_datetime)


@plugin.on_commands(['датарег', 'reg_date'])
@chat_only
async def _(msg, ctx):
    users = await extract_users(msg, ctx)
    if users:
        user_id = users[0]
    else:
        user_id = msg.sender_id
    reg_datetime = await get_registration_date(user_id)
    user_time, user_date = format_registration_date(reg_datetime)

    user_vk = (await ctx.request('users.get', {'user_ids': user_id, 'name_case': 'gen'}))[0]
    ctx.reply(f'Страница {user_vk["first_name"]} {user_vk["last_name"]} зарегистрирована {user_date} в {user_time}')
