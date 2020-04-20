from kutana import Plugin, Context, Message


plugin = Plugin(name='Аы', description='Напиши мне кто ты и я скажу кто ты')


@plugin.on_commands(['аы', 'шуе'])
async def _(msg: Message, ctx: Context):
    await ctx.reply(ctx.body.capitalize())
