from kutana import HandlerResponse

from bot.roles import needed_admin_rights
from bot.plugin import CustomPlugin
from bot.router import AnyMessageRouterCustom

plugin = CustomPlugin('Hello message')


@plugin.on_router(AnyMessageRouterCustom)
@needed_admin_rights
async def _(msg, ctx):
    if not hasattr(ctx, 'chat'):
        return HandlerResponse.SKIPPED
    if not msg.raw['object']['message'].get('action', {'type': ''})['type'].startswith('chat_invite_user'):
        return HandlerResponse.SKIPPED
    await ctx.reply('КУ!')
