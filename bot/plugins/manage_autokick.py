from kutana import Message, HandlerResponse

from bot.plugin import CustomPlugin as Plugin
from bot.plugins.kick import kick_users
from bot.roles import admin_role, needed_admin_rights, chat_only
from bot.utils import on_or_off

plugin = Plugin('Autokick', 'Автокик вышедших')


@plugin.on_commands(['автокик', 'autokick'])
@chat_only
@admin_role
async def _(msg, ctx):
    if ctx.body:
        msg = ctx.body.lower()
        action = on_or_off(msg)
        if action is not None:
            ctx.chat.kick_left = bool(action)
            await ctx.mgr.update(ctx.chat)
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
