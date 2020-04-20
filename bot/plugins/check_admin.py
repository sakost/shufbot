from kutana import Plugin, Context
from kutana.exceptions import RequestException


plugin = Plugin('Check admin rights', 'Проверяет, есть ли права Администратора у бота')


@plugin.on_commands(['чекадм', 'check_access', 'check_admin'])
async def _(msg, ctx: Context):
    try:
        resp = await ctx.request('messages.getConversationMembers', peer_id=msg.receiver_id)
    except RequestException as e:
        await ctx.reply('Я не админ :с')
    else:
        for member in resp['items']:
            if member['member_id'] == -ctx.backend.group_id:
                await ctx.reply('Я админ.. хе-хе' if member['is_admin'] else 'Я не админ :с')
                break
