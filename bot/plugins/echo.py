from kutana import Context, Message
from bot.plugin import CustomPlugin as Plugin

plugin = Plugin(name='Аы', description='Напиши мне кто ты и я скажу кто ты')


@plugin.on_commands(['аы', 'шуе', 'ыа', 'ку', 'ыы', 'шпш'])
async def _(msg: Message, ctx: Context):
    await ctx.reply(ctx.command.capitalize())
