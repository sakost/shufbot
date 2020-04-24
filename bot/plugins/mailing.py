import asyncio

from kutana.exceptions import RequestException

from bot.plugin import CustomPlugin as Plugin
from bot.roles import developer_global_role
from bot.db import Chat


plugin = Plugin('Mailing[develop]', 'отправляет рассылку по всем чатам')


@plugin.on_commands(['рассылка', 'mail'])
@developer_global_role
async def _(msg, ctx):
    text: str = ctx.body
    chats = await ctx.mgr.execute(Chat.select())
    for chat in chats:
        # maybe kicked from several chats
        try:
            await ctx.send_message(chat.id, "Рассылка от разработчиков:\n" + text)
        except RequestException as e:
            pass
        # let other stuff to work
        await asyncio.sleep(0)


