from kutana import Plugin, HandlerResponse

from bot.roles import needed_admin_rights

plugin = Plugin('Hello message')


@plugin.on_any_message(priority=-1)
@needed_admin_rights
async def _(msg, ctx):
    if not hasattr(ctx, 'chat'):
        return HandlerResponse.SKIPPED
    if not msg.raw['object']['message'].get('action', {'type': ''})['type'].startswith('chat_invite_user'):
        return HandlerResponse.SKIPPED
    await ctx.reply('КУ!')
