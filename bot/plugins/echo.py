from kutana import Plugin, Context, Message


plugin = Plugin(name='Echo', description='Напиши мне кто ты и я скажу кто ты')


@plugin.on_commands(['эхо', 'echo'])
async def _(msg: Message, ctx: Context):
    await ctx.reply(ctx.body, attachments=msg.attachments)
