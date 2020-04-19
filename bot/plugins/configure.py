from peewee_async import Manager

from kutana import Plugin, Kutana, Update, UpdateType, Context
from kutana.update import ReceiverType

from bot.db import ChatUser, User, Chat

plugin = Plugin('Configure[system]')


async def init_db(app: Kutana):
    app.config['db_manager'] = Manager(app.config['database'], loop=app.get_loop())


@plugin.on_start()
async def _(app: Kutana):
    for backend in app.get_backends():
        if backend.get_identity() == 'vkontakte':
            app.config['owner_id'] = (await backend.resolve_screen_name(app.config['settings']['OWNER_ID']))['object_id']
            await init_db(app)
            break


@plugin.on_before()
async def _(upd: Update, ctx: Context):
    if upd.type == UpdateType.MSG:
        user_id = upd.raw['object']['message']['from_id']
        mgr = ctx.config['db_manager']
        ctx.user, created = await mgr.get_or_create(User, id=user_id)
        if upd.receiver_type == ReceiverType.MULTI:
            ctx.chat, chat_created = await mgr.get_or_create(Chat, id=upd.receiver_id)
            ctx.chat_user, chat_user_created = await mgr.get_or_create(ChatUser, id=user_id, chat=ctx.chat)


@plugin.on_shutdown()
async def _(app: Kutana):
    await app.config['db_manager'].close()
