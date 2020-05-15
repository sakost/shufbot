from kutana import Plugin

from bot.router import ActionMessageRouter, AnyMessageRouterCustom


class CustomPlugin(Plugin):
    def on_router(self, custom_router, group_state='*', user_state='*', priority=0, **kwargs):
        def decorator(func):
            self._add_handler_for_router(
                custom_router,
                handler=self._make_handler(func, group_state, user_state, priority),
                **kwargs,
            )
            return func

        return decorator

    def on_message_action(self, action_type, priority=7, **kwargs):
        return self.on_router(ActionMessageRouter, priority=priority, handler_key=action_type, **kwargs)

    def on_any_message(self, group_state="*", user_state="*", priority=0, router_priority=None):
        def decorator(func):
            self._add_handler_for_router(
                AnyMessageRouterCustom,
                handler=self._make_handler(func, group_state, user_state, priority),
                router_priority=router_priority,
            )
            return func
        return decorator
