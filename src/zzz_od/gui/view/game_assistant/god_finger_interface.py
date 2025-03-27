from one_dragon_qt.view.app_run_interface import AppRunInterface
from zzz_od.application.zzz_application import ZApplication
from zzz_od.context.zzz_context import ZContext
from one_dragon.base.operation.application_base import Application
from zzz_od.application.god_finger.god_finger_app import GodFingerApp

class GodFingerInterface(AppRunInterface):

    def __init__(self,
                 ctx,
                 parent=None):
        self.ctx = ctx
        self.app = None

        AppRunInterface.__init__(
            self,
            ctx=ctx,
            object_name='god_finger_interface',
            nav_text_cn='金手指',
            parent=parent,
        )

    def get_widget_at_top(self):
        pass

    def on_interface_shown(self):
        AppRunInterface.on_interface_shown(self)

    def get_app(self) -> Application:
        return GodFingerApp(self.ctx)