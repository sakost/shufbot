from kutana import Plugin

plugin = Plugin('Unknown command')


@plugin.on_any_unprocessed_message()
async def _(msg, ctx):
    for prefix in ctx.config['prefixes']:
        if msg.text.startswith(prefix):
            await ctx.reply('Неизвестная команда')
            return
