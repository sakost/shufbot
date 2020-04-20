from kutana import Plugin
from kutana.handler import Handler


class CustomPlugin(Plugin):
    def on_router(self, custom_router, group_state='*', user_state='*', priority=0):
        def decorator(func):
            router = self._get_or_add_router(custom_router)
            router.add_handler(
                Handler(func, group_state, user_state, priority),
            )
            return func

        return decorator
