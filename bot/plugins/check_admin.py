from kutana import Plugin, Context
from kutana.exceptions import RequestException

from bot.roles import chat_only

plugin = Plugin('Check admin rights', 'Проверяет, есть ли права Администратора у бота')


@plugin.on_commands(['чекадм', 'check_access', 'check_admin'])
@chat_only()
async def _(msg, ctx: Context):
    peer_id = msg.receiver_id
    try:
        await ctx.request('messages.getConversationMembers', peer_id=peer_id)
    except RequestException as e:
        await ctx.reply('Я не админ :с')
        ctx.chat.admin = False
    else:
        await ctx.reply('Я админ.. хе-хе')
        ctx.chat.admin = True
    await ctx.mgr.update(ctx.chat)
