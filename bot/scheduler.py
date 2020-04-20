import time
from datetime import datetime, timedelta

import asyncio
from aiojobs import create_scheduler
from peewee_async import Manager

from bot.db import Chat
from bot.roles import ChatRoles


async def compute_stat(app) -> str:
    return "stub"


def calculate_sleep_time(dt: datetime):
    return dt.timestamp() - time.time()


async def inform(app):
    inform_time = app.config['inform_time']
    if datetime.now().time() < inform_time:
        next_dt = datetime.combine(datetime.now().date(), inform_time)
    else:
        next_dt = datetime.combine((datetime.now() + timedelta(days=1)).date(), inform_time)
    await asyncio.sleep(calculate_sleep_time(next_dt))
    for backend in app.get_backend():
        if backend.get_identity() == 'vkontakte':
            mgr: Manager = app.config['db_manager']
            chats = await mgr.execute(Chat.select(Chat.level == ChatRoles.DEVELOPER.value))
            for chat in chats:
                await backend.send_message(chat.get_id, '[Автоинформирование]\n' + await compute_stat(app))
            break
    await app.scheduler.spawn(inform(app))


async def init_scheduler(app):
    app.scheduler = await create_scheduler()
    await app.scheduler.spawn(inform(app))

