from kutana import Message, HandlerResponse

from bot.plugin import CustomPlugin as Plugin
from bot.plugins.kick import kick_users
from bot.roles import admin_role, needed_admin_rights, chat_only

plugin = Plugin('Autokick', 'Автокик вышедших')

COMMANDS = {
    'on': 1,
    'off': 0,
    'вкл': 1,
    'выкл': 0,
}


@plugin.on_commands(['автокик', 'autokick'])
@chat_only
@admin_role
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        for cmd in COMMANDS:
            if msg.startswith(cmd):
                action = COMMANDS[cmd]
                ctx.chat.kick_left = bool(action)
                await ctx.mgr.update(ctx.chat)
                break
    await ctx.reply(f'Автокик {"включен" if ctx.chat.kick_left else "выключен"}')


@plugin.on_message_action('chat_kick_user')
@chat_only
@needed_admin_rights
async def _(msg: Message, ctx):
    if not hasattr(ctx, 'chat'):
        return HandlerResponse.SKIPPED

    if not ctx.chat.kick_left:
        return HandlerResponse.SKIPPED

    # somebody kicked user
    if ctx.action['member_id'] != msg.sender_id:
        return HandlerResponse.SKIPPED

    await kick_users(ctx, [(ctx.user, ctx.chat_user)], msg.receiver_id - 2 * 10 ** 9)
