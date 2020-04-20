from kutana.routers import AnyMessageRouter
from kutana.update import UpdateType


class AnyMessageRouterCustom(AnyMessageRouter):
    def _check_update(self, update, ctx):
        return update.type == UpdateType.MSG


