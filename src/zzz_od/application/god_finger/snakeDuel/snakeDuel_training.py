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
from one_dragon.utils.log_utils import log

class ArcadeSnakeDuelTraining(ZApplication):

    def __init__(self, ctx: ZContext, env, total_episodes: int):
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

        self.env = env

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
    @operation_node(name='训练金手指')
    def train_agent(self) -> OperationRoundResult:
        ACTION_SPACE = ['w', 'a', 's', 'd', 'j', None]
        state, game_over_flag = self.env.reset()


        while game_over_flag is False:
            # TODO: 加入agent
            # action = self.agent.get_action(state)
            action = np.random.choice(ACTION_SPACE)

            state, reward, game_over_flag = self.env.step(action)

            # Show training info
            action_str = f"{action:>4}" if action is not None else "None"
            log.info(f"Episode: {self.finish_episodes}, Action: {action_str}, Game Over: {str(game_over_flag):>5}, Reward: {reward}")

        self.finish_episodes += 1
        if self.finish_episodes >= self.total_episodes:
            return self.round_success(status='训练完成', wait=1)
        else:
            return self.round_success(status='训练继续', wait=1)
        
    @node_from(from_name='训练金手指', status='训练继续')
    @operation_node(name='点击再次挑战', node_max_retry_times=20)
    def click_play_again(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '电玩店-蛇对蛇', '再次挑战',
                                                   success_wait=1, retry_wait=1)
        return result
        
    @node_from(from_name='训练金手指', status='训练完成')
    @operation_node(name='点击返回', node_max_retry_times=20)
    def click_back(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '电玩店-蛇对蛇', '返回',
                                                   success_wait=1, retry_wait=1)
        return result

    
def _debug():
    ctx = ZContext()
    ctx.init_by_config()

    # env_ctx = ZContext()
    # env_ctx.init_by_config()
    # env = SnakeDuelEnv(env_ctx)
    env = SnakeDuelEnv(ctx)
    app = ArcadeSnakeDuelTraining(ctx, env, total_episodes=1)
    app.execute()

if __name__ == '__main__':
    _debug()
    

