import re

from kutana import Plugin, Kutana, Update, UpdateType, Context, HandlerResponse
from kutana.update import ReceiverType
from peewee_async import Manager

from bot.db import ChatUser, User, Chat
from bot.scheduler import init_scheduler
from bot.roles import ChatRoles

plugin = Plugin('Configure[system]')


async def init_db(app: Kutana):
    app.config['db_manager'] = Manager(app.config['database'], loop=app.get_loop())


@plugin.on_start()
async def _(app: Kutana):
    for backend in app.get_backends():
        if backend.get_identity() == 'vkontakte':
            app.config['owner_id'] = (await backend.resolve_screen_name(app.config['settings']['OWNER_ID']))[
                'object_id']
            await init_db(app)
            # order is important
            await init_scheduler(app)
            break
    app.config['re_chat_prefixes'] = re.compile(rf'^({"|".join(map(re.escape, app.config["chat_prefixes"]))})\s*?(.*)$',
                                                re.IGNORECASE | re.UNICODE)


@plugin.on_before()
async def _(upd: Update, ctx: Context):
    if upd.type == UpdateType.MSG:
        message = upd.raw['object']['message']
        user_id = message['from_id']
        ctx.mgr: Manager = ctx.config['db_manager']

        # define shortcuts to chat and user
        ctx.user, created = await ctx.mgr.get_or_create(User, id=user_id)
        ctx.is_chat = False
        if upd.receiver_type == ReceiverType.MULTI:
            ctx.chat, chat_created = await ctx.mgr.get_or_create(Chat, id=upd.receiver_id - 2*10**9)
            ctx.chat_user, chat_user_created = await ctx.mgr.get_or_create(ChatUser, user=ctx.user, chat=ctx.chat)
            ctx.is_chat = True


@plugin.on_any_update(router_priority=50)
async def _(upd, ctx):
    if upd.type == UpdateType.MSG:
        ctx.with_prefix = False
        message = upd.raw['object']['message']
        if (match := ctx.app.config['re_chat_prefixes'].match(message.get('text', ''))) is not None:
            message['text'] = match.group(2)
            ctx.with_prefix = True
        elif ctx.is_chat and ctx.chat.mention:
            return
    return HandlerResponse.SKIPPED


@plugin.on_shutdown()
async def _(app: Kutana):
    await app.config['db_manager'].close()
    await app.config['scheduler'].close()


@plugin.on_exception()
async def _(upd, ctx: Context, exc: Exception):
    await ctx.reply('Что-то пошло не так...')
    if ctx.chat.level >= ChatRoles.DEVELOPER:
        await ctx.reply(repr(exc))
    else:
        await ctx.send_message(ctx.config['owner_id'], repr(exc))
