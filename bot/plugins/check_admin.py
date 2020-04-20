from kutana import Plugin, Context
from kutana.exceptions import RequestException

from bot.db import Chat


plugin = Plugin('Check admin rights', 'Проверяет, есть ли права Администратора у бота')


@plugin.on_commands(['чекадм', 'check_access', 'check_admin'])
async def _(msg, ctx: Context):
    mgr = ctx.config['db_manager']
    peer_id = msg.receiver_id
    try:
        resp = await ctx.request('messages.getConversationMembers', peer_id=peer_id)
    except RequestException as e:
        await ctx.reply('Я не админ :с')
    else:
        await ctx.reply('Я админ.. хе-хе')
        chat, created = await mgr.get_or_create(Chat, id=peer_id)
        chat.admin = True
        await mgr.update(chat)
