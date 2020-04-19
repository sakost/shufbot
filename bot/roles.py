from enum import IntEnum, auto
from functools import wraps

from peewee_async import Manager

from bot.db import User, ChatUser


class ChatRoles(IntEnum):
    USER = 0
    VIP_USER = auto()
    ADMIN = auto()
    CREATOR = auto()


class Roles(IntEnum):
    USER = 0
    DONATER = auto()
    DEVELOPER = auto()
    OWNER = auto()


def is_owner(user_id, config):
    return user_id == config['owner_id']


def restrict_access(level, global_=False):
    """
    :param level is the Role or ChatRole from this scope
    :param global_ is whether use global settings for user or not. ChatRoles for default
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            msg, ctx, *_ = args
            user_id = msg.sender_id

            mgr: Manager = ctx.config['db_manager']
            if global_:
                user, created = await mgr.get_or_create(User, id=user_id)
            else:
                user, created = await mgr.get_or_create(ChatUser, id=user_id)

            if is_owner(user_id, ctx.config):
                if user.role != Roles.OWNER.value:
                    user.role = Roles.OWNER.value
                    await mgr.update(user)
                return await func(*args, **kwargs)
            if user.role >= level.value:
                return await func(*args, **kwargs)
            await ctx.reply("У вас недостаточно прав для этой команды!")
        return wrapper
    return decorator


def owner_global_role(func):
    return restrict_access(Roles.OWNER, global_=True)(func)


def developer_global_role(func):
    return restrict_access(Roles.DEVELOPER, global_=True)(func)


def donater_global_role(func):
    return restrict_access(Roles.DONATER, global_=True)(func)


def creator_role(func):
    return restrict_access(ChatRoles.CREATOR)(func)


def admin_role(func):
    return restrict_access(ChatRoles.ADMIN)(func)


def vip_role(func):
    return restrict_access(ChatRoles.VIP_USER)(func)

