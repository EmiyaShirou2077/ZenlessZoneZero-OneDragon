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
import os

class ArcadeSnakeDuelTraining(ZApplication):

    def __init__(self, ctx: ZContext, env, agent, total_episodes: int):
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
        self.agent = agent
        self.action = None

    def handle_init(self):
        self.finish_episodes: int = 0  # 完成次数
        self.listen_btn()

    @operation_node(name='点击开始游戏', node_max_retry_times=20)
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
        # print('state', state.shape, state.dtype)
        # return self.round_success()

        while game_over_flag is False:
            # Type 1: agent training from scratch
            agent_action = self.agent.get_action(state)
            # Type 2: agent training with human input
            action = self.action
            self.action = None  # Reset action after reading

            # get feedback from the environment when taking action at state
            next_state, reward, game_over_flag = self.env.step(self.action)
            # update the agent
            self.agent.remember(state, action, reward, next_state, game_over_flag)
            self.agent.train_step()

            state = next_state

            # Show training info
            action_str = f"{action:>4}" if action is not None else "None"
            agent_action_str = f"{agent_action:>4}"
            log.info(f"Total Episodes: {self.agent.episodes}, Episode: {self.finish_episodes}, User Action: {action_str}, Agent Action: {agent_action_str}, Game Over: {str(game_over_flag):>5}, Reward: {reward}")

        # Save model every N steps
        if self.finish_episodes % 1 == 0:
            self.agent.episodes += 1
            self.agent.save(self.agent.model_path)

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
    
    def listen_btn(self) -> None:
        self.ctx.listen_event(ContextKeyboardEventEnum.PRESS.value, self._on_key_press)
    def _on_key_press(self, key: str):
        """
        按键时触发 抛出事件，事件体为按键
        :param key: 按键
        :return:
        """
        # log.info('按键 %s' % key.data)
        if key.data in ['w', 'a', 's', 'd', 'j']:
            self.action = key.data
        else:
            self.action = None

def _debug():
    ctx = ZContext()
    ctx.init_by_config()

    # env_ctx = ZContext()
    # env_ctx.init_by_config()
    # env = SnakeDuelEnv(env_ctx)
    env = SnakeDuelEnv(ctx)
    path = os.path.dirname(os.path.abspath(__file__))
    ACTION_SPACE = ['w', 'a', 's', 'd', 'j', None]

    agent_path = os.path.join(path, "snakeDuel_agent.pth")
    agent = SnakeDuelAgent(ACTION_SPACE, epsilon=0.0, model_path=agent_path)
    app = ArcadeSnakeDuelTraining(ctx, env, agent, total_episodes=1000)
    app.execute()

if __name__ == '__main__':
    _debug()
    

