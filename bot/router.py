from kutana.router import MapRouter
from kutana.routers import AnyMessageRouter
from kutana.update import UpdateType


class AnyMessageRouterCustom(AnyMessageRouter):
    def _check_update(self, update, ctx):
        return update.type == UpdateType.MSG

class AnyMessageRouterCustom(AnyMessageRouter):
    def _check_update(self, update, ctx):
        return update.type == UpdateType.MSG

class ActionMessageRouter(MapRouter):
    __slots__ = ()

    def __init__(self, priority=7):
        """Base priority is 7."""
        super().__init__(priority)

    def add_handler(self, handler, key):
        return super().add_handler(handler, key.lower())

    def _get_keys(self, update, ctx):
        if update.type != UpdateType.MSG:
            return ()
        if (action := update.raw['object']['message'].get('action', None)) is None:
            return ()
        ctx.action_type = action['type']
        ctx.action = action
        return action['type'],
