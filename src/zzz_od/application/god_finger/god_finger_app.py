import time

from cv2.typing import MatLike
from typing import Optional

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.context_event_bus import ContextEventItem
from one_dragon.base.operation.one_dragon_context import ContextKeyboardEventEnum
from one_dragon.base.operation.operation_base import OperationResult
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult, OperationRoundResultEnum
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from zzz_od.application.commission_assistant.commission_assistant_config import DialogOptionEnum, StoryMode
from zzz_od.application.zzz_application import ZApplication
from zzz_od.auto_battle import auto_battle_utils
from zzz_od.auto_battle.auto_battle_operator import AutoBattleOperator
from zzz_od.context.zzz_context import ZContext
from zzz_od.hollow_zero.event import hollow_event_utils
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.operation.transport import Transport
from one_dragon.base.operation.context_event_bus import ContextEventItem
from one_dragon.base.operation.one_dragon_context import ContextKeyboardEventEnum




class GodFingerApp(ZApplication):
    
    def __init__(self, ctx):
        ZApplication.__init__(
            self,
            ctx=ctx, app_id='god_finger',
            op_name='金手指',
            retry_in_od=False,
        )
    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        pass
    
    # @operation_node(name='传送', is_start_node=True)
    # def tp(self) -> OperationRoundResult:
    #     op = Transport(self.ctx, '六分街', '电玩店')
    #     return self.round_by_op_result(op.execute())
    
    # @node_from(from_name='传送')
    @operation_node(name="按下W键", is_start_node=True)
    def press_w_key(self) -> OperationRoundResult:
        self.ctx.controller.move_w(press=True, press_time=0.1, release=True)
        time.sleep(0.5)
        return self.round_success()
    
    @node_from(from_name='按下W键')
    @operation_node(name="按下A键")
    def press_a_key(self) -> OperationRoundResult:
        self.ctx.controller.move_a(press=True, press_time=0.1, release=True)
        time.sleep(0.5)

        return self.round_success()




def __debug():
    ctx = ZContext()
    ctx.init_by_config()

    app = GodFingerApp(ctx)
    app.execute()

if __name__ == '__main__':
    __debug()