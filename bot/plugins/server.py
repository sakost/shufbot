import os
import time

import psutil
import aioping

from kutana import Plugin

from bot.roles import admin_role

plugin = Plugin('Server[admin]', 'pings to servers')


@plugin.on_commands(['метрик', 'server', 'серв', 'metrics'])
@admin_role
async def _(msg, ctx):
    p = psutil.cpu_percent(interval=1, percpu=True)
    cur_process = psutil.Process(os.getpid())
    m = psutil.virtual_memory()
    answer = ''
    for num, process in enumerate(p):
        answer += f'CPU[{num}]: {process}%\n'
    answer += f'RAM: {m.percent}% от {int(m.total/(10**9))} GB\n'
    try:
        answer += f"Ping(vk): {(await aioping.ping('vk.com'))*1000:.2f} ms\n"
    except TimeoutError:
        answer += f"Ping(vk): >10sec\n"
    try:
        answer += f"Ping(vk api): {(await aioping.ping('api.vk.com')) * 1000:.2f} ms\n"
    except TimeoutError:
        answer += f"Ping(vk api): >10sec"
    answer += f"Бот занимает: {cur_process.memory_info().rss / 2**20:.2f}MiB памяти\n"
    elapsed_time = int(time.time()) - msg.date
    if elapsed_time > 0:
        answer += f'Прошло {elapsed_time} секунд с момента получения сообщения\n'
    await ctx.reply(answer)
