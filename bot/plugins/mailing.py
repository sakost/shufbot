import asyncio

from kutana.exceptions import RequestException

from bot.db import Chat
from bot.plugin import CustomPlugin as Plugin
from bot.roles import developer_global_role, creator_role, chat_only
from bot.utils import on_or_off

plugin = Plugin('Mailing[develop]', 'отправляет рассылку по всем чатам')


@plugin.on_commands(['рассылка', 'mail'])
@developer_global_role
async def _(msg, ctx):
    text: str = ctx.body
    chats = await ctx.mgr.execute(Chat.select())
    for chat in chats:
        if not chat.enabled_mailing:
            continue
        # maybe kicked from several chats
        try:
            await ctx.send_message(chat.id, "Рассылка от разработчиков:\n" + text)
        except RequestException as e:
            pass
        # let other stuff to work
        await asyncio.sleep(0)


@plugin.on_commands(['set_mail'])
@chat_only()
@creator_role
async def _(msg, ctx):
    text = ctx.body
    on = on_or_off(text)
    if on is None:
        await ctx.reply('Неизвестная инструкция. Напишите выкл/off или вкл/on')
        return
    ctx.chat.enabled_mailing = on
    await ctx.mgr.update(ctx.chat)
    if on:
        await ctx.reply('В этом чате разрешена рассылка от разработчиков')
    else:
        await ctx.reply('В этом чате запрещена рассылка от разработчиков')
