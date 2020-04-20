import re

import asyncio

EXTRACT_USERS_MENTIONED = re.compile(r'\[id(\d*?)\|.*?\]', re.DOTALL)
EXTRACT_USERS_URLS = re.compile(r'(https?://)?(www\.)?vk\.com/(?P<username>[^\s]+)', re.DOTALL)


async def extract_users_urls(ctx):
    text = ctx.body
    users = []
    for user_match in EXTRACT_USERS_URLS.finditer(text):
        user = await ctx.resolve_screen_name(user_match.group('username'))
        if user.get('type', None) == 'user':
            users.append(user['object_id'])
    return users


async def extract_mentioned_users(ctx):
    text = ctx.body
    users = []
    for user_match in EXTRACT_USERS_MENTIONED.finditer(text):
        users.append(int(user_match.group(1)))
    return users


async def extract_users(msg, ctx):
    users = []
    if not ctx.body:
        raw_msg = msg.raw['object']['message']
        reply_msg = raw_msg.get('reply_message', None)
        fwd_messages = raw_msg.get('fwd_messages', [])

        if reply_msg is not None:
            users.append(reply_msg['from_id'])

        for fwd_msg in fwd_messages:
            users.append(fwd_msg['from_id'])
        # let other coroutines to work
        await asyncio.sleep(0)
    users.extend(await extract_mentioned_users(ctx))
    await asyncio.sleep(0)
    users.extend(await extract_users_urls(ctx))
    await asyncio.sleep(0)
    return users