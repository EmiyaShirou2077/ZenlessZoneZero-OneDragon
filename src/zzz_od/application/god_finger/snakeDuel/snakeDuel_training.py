from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from zzz_od.context.zzz_context import ZContext
from zzz_od.operation.arcade.arcade_start_game import ArcadeStartGame
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.application.zzz_application import ZApplication
from zzz_od.application.god_finger.snakeDuel.snakeDuel_env import SnakeDuelEnv
from zzz_od.application.god_finger.snakeDuel.snakeDuel_agent import SnakeDuelAgent
from one_dragon.base.operation.one_dragon_context import ContextKeyboardEventEnum
from one_dragon.base.operation.context_event_bus import ContextEventItem
from zzz_od.context.zzz_context import ZContext
from one_dragon.utils import debug_utils, cv2_utils
import time
import numpy as np

class ArcadeSnakeDuelTraining(ZApplication):

    def __init__(self, ctx: ZContext, total_episodes: int):
        """
        蛇对蛇训练
        :param ctx:
        """
        ZApplication.__init__(
            self, 
            ctx=ctx, app_id='god_finger',
            op_name=gt('蛇对蛇训练', 'ui')
            )
        self.total_episodes: int = total_episodes # 所需的训练次数
        self.finish_episodes: int = 0  # 完成的训练次数

        self.env = SnakeDuelEnv(self)  # 蛇对蛇环境

    def handle_init(self):
        self.finish_episodes: int = 0  # 完成次数

    @operation_node(name='点击开始游戏')
    def click_start(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(
            screen, '电玩店', '开始游戏',
            success_wait=1, retry_wait=1
        )
        return result
    
    @node_from(from_name='点击开始游戏')
    @operation_node(name='等待加载', node_max_retry_times=20)
    def wait_game_load(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_area(screen, '电玩店-蛇对蛇', '加载完成', retry_wait=1)
    
    @node_from(from_name='等待加载')
    @node_from(from_name='点击再次挑战')
    @operation_node(name='游戏开始', node_max_retry_times=20)
    def game_start(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_area(screen, '电玩店-蛇对蛇', '游戏开始', retry_wait=1)
    
    @node_from(from_name='游戏开始')
    @node_from(from_name='检查游戏是否结束', status='游戏未结束')
    @operation_node(name='训练金手指')
    def train_agent(self) -> OperationRoundResult:
        # self.env.reset()
        # flag_game_over = False
        # state = self.env.get_state()
        # action = self.env.action_space.sample()

        # # TODO: 加入agent
        # # action = self.agent.get_action(state)
        # while not flag_game_over:
        #     state, reward, flag_game_over = self.env.step(action)

        #     if flag_game_over:
        #         break
        ACTION_SPACE = ['w', 'a', 's', 'd', 'j', 'none']
        action = np.random.choice(ACTION_SPACE)
        if action == 'none':
            time.sleep(0.1)
        else:
            self.ctx.controller.keyboard_controller.press(action, press_time=0.1)

        # self.finish_episodes += 1


        return self.round_success()
    
    @node_from(from_name='训练金手指')
    @operation_node(name='检查游戏是否结束')
    def check_game_over(self) -> OperationRoundResult:
        screen = self.screenshot()
        game_over_flag = self.round_by_find_area(screen, '电玩店-蛇对蛇', '游戏结束').is_success
        print(game_over_flag)
        if game_over_flag:
            self.finish_episodes += 1
            if self.finish_episodes >= self.total_episodes:
                return self.round_success(status='游戏结束-训练完成', wait=1)
            else:
                return self.round_success(status='游戏结束-训练继续', wait=1)
        else:
            return self.round_success(status='游戏未结束')
        
    @node_from(from_name='检查游戏是否结束', status='游戏结束-训练继续')
    @operation_node(name='点击再次挑战', node_max_retry_times=20)
    def click_play_again(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '电玩店-蛇对蛇', '再次挑战',
                                                   success_wait=1, retry_wait=1)
        return result
        
    @node_from(from_name='检查游戏是否结束', status='游戏结束-训练完成')
    @operation_node(name='点击返回', node_max_retry_times=20)
    def click_back(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '电玩店-蛇对蛇', '返回',
                                                   success_wait=1, retry_wait=1)
        return result

    
def _debug():
    ctx = ZContext()
    ctx.init_by_config()

    app = ArcadeSnakeDuelTraining(ctx, total_episodes=3)
    app.execute()

if __name__ == '__main__':
    _debug()
    

