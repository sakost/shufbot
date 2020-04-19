from kutana import Plugin, Context, Message


plugin = Plugin(name='Echo', description='Напиши мне кто ты и я скажу кто ты')


@plugin.on_commands(['ае', 'ae'])
async def _(msg: Message, ctx: Context):
    await ctx.reply('Ае')
