from functools import wraps


def admin_role(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        msg, ctx, *_ = args
        if ctx.config['owner_id'] != msg.raw['object']['message']['from_id']:
            ctx.reply('У вас недостаточно прав для этой команды!')
            return
        return await func(*args, **kwargs)
    return wrapper
