from kutana import Plugin

from bot.db import ChatUser, User
from bot.roles import admin_role, needed_admin_rights, chat_only
from bot.utils import get_avatares_and_names, extract_mesasges

plugin = Plugin('Цитата', 'Создает цитату из сообщений')


@plugin.on_commands(['цит', 'quote'])
async def _(msg, ctx):
    messages = await extract_mesasges(msg, ctx)
    if not messages:
        await ctx.reply('Вы не указали сообщения для цитаты')
    user_ids = [i["from_id"] for i in messages]
    users = await get_avatares_and_names(ctx, user_ids)
    last_id = 0
    message = ""
    for i in messages:
        id = i["from_id"]
        message = i["text"]
        if id != last_id:
            message += users[id]["name"] + ":\n"
        message += "> " + message + "\n"
        last_id = i["from_id"]
    