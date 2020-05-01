from enum import IntEnum, auto
from functools import wraps

from kutana import HandlerResponse
from kutana.exceptions import RequestException
from peewee_async import Manager


class ChatRoles(IntEnum):
    NORMAL = 0
    IMPROVED = auto()
    DEVELOPER = auto()


class ChatUserRoles(IntEnum):
    USER = 0
    VIP_USER = auto()
    ADMIN = auto()
    CREATOR = auto()


class UserRoles(IntEnum):
    USER = 0
    DONATER = auto()
    DEVELOPER = auto()
    OWNER = auto()


def restrict_chat_access(level):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            msg, ctx, *_ = args
            if level.value < ctx.chat.level:
                return HandlerResponse.SKIPPED
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def is_owner(user_id, config):
    return user_id == config['owner_id']


def restrict_access(level, global_=False):
    """
    :param level is the Role or ChatRole from this scope
    :param global_ is whether use global settings for user or not. ChatUserRoles for default
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            msg, ctx, *_ = args
            user_id = msg.sender_id

            mgr: Manager = ctx.mgr

            user = ctx.user
            if not global_:
                user = ctx.chat_user

            if is_owner(user_id, ctx.config):
                if global_ and user.role != UserRoles.OWNER.value:
                    user.role = UserRoles.OWNER.value
                    await mgr.update(user)
                return await func(*args, **kwargs)
            if user.role >= level.value:
                return await func(*args, **kwargs)
            await ctx.reply("У вас недостаточно прав для этой команды!")

        return wrapper

    return decorator


def owner_global_role(func):
    return restrict_access(UserRoles.OWNER, global_=True)(func)


def developer_global_role(func):
    return restrict_access(UserRoles.DEVELOPER, global_=True)(func)


def donater_global_role(func):
    return restrict_access(UserRoles.DONATER, global_=True)(func)


def creator_role(func):
    return restrict_access(ChatUserRoles.CREATOR)(func)


def admin_role(func):
    return restrict_access(ChatUserRoles.ADMIN)(func)


def vip_role(func):
    return restrict_access(ChatUserRoles.VIP_USER)(func)


def needed_admin_rights(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        msg, ctx, *_ = args
        try:
            return await func(*args, **kwargs)
        except RequestException as e:
            if e.error.get('error_code', -1) not in (917, 925, 15):
                raise
            await ctx.reply('У бота недостаточно прав для этого действия')

    return wrapper


def chat_only(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        msg, ctx, *_ = args
        if not hasattr(ctx, 'chat') or not hasattr(ctx, 'chat_user'):
            await ctx.reply('Чат не является беседой')
            return
        return await func(*args, **kwargs)

    return wrapper
