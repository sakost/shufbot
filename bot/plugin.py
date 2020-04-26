from kutana import Plugin
from kutana.handler import Handler

from bot.router import ActionMessageRouter


class CustomPlugin(Plugin):
    def on_router(self, custom_router, group_state='*', user_state='*', priority=0, **kwargs):
        def decorator(func):
            router = self._get_or_add_router(custom_router)
            router.add_handler(
                Handler(func, group_state, user_state, priority),
                **kwargs
            )
            return func

        return decorator

    def on_message_action(self, action_type, priority=7, **kwargs):
        return self.on_router(ActionMessageRouter, priority=priority, key=action_type, **kwargs)
