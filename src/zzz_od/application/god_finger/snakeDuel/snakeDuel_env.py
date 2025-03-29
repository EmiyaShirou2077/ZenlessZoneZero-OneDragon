import numpy as np
import cv2
import time
from one_dragon.base.controller.pc_button.pc_button_controller import PcButtonController
from one_dragon.utils import os_utils, cv2_utils, str_utils
from zzz_od.application.zzz_application import ZApplication
from zzz_od.context.zzz_context import ZContext
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt







class SnakeDuelEnv(ZApplication):
    def __init__(self, ctx: ZContext):
        """
        蛇对蛇环境
        """
        ZApplication.__init__(
            self, ctx=ctx, app_id='snakeDuel_env', op_name=gt('蛇对蛇环境', 'ui')
        )
        self.last_score = 0

    def reset(self):
        self.last_score = 0
        screen = self.screenshot()
        state = self.get_state(screen)
        game_over_flag = self.check_game_over(screen)
        return state, game_over_flag

    def step(self, action):
        if action is None:
            time.sleep(0.1)
        else:
            self.press_key(action)
        time.sleep(0.2)

        screen = self.screenshot()
        # check if game over
        game_over_flag = self.check_game_over(screen)
        if game_over_flag:
            return None, -999999999, game_over_flag
        else:
            # print('game_over_flag', game_over_flag)
            state = self.get_state(screen)
            score = self.get_score(screen)
            reward = self.get_reward(score)
            self.last_score = score
            return state, reward, game_over_flag

    def press_key(self, key: str):
        self.ctx.controller.btn_controller.press(key, press_time=0.1)

    def get_score(self, screen):
        '''
        获取街机游戏分数
        '''
        area = self.ctx.screen_loader.get_area('电玩店-蛇对蛇', '分数')
        score_img = cv2_utils.crop_image_only(screen, area.rect)
        score_str = self.ctx.ocr.run_ocr_single_line(score_img)
        # print(score_str)
        if score_str == '':
            cv2.imwrite('score.png', screen)
        score = int(score_str.replace(' ', ''))
        return score

    def get_state(self, screen):
        '''
        获取街机游戏界面(State)
        '''
        area = self.ctx.screen_loader.get_area('电玩店-蛇对蛇', '游戏界面')
        state = cv2_utils.crop_image_only(screen, area.rect)
        return state
    

    def get_reward(self, current_score):
        reward = current_score - self.last_score
        return reward

    def check_game_over(self, screen) -> OperationRoundResult:
        # cv2.imwrite('game_over.png', screen)
        area = self.ctx.screen_loader.get_area('电玩店-蛇对蛇', '游戏结束')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        # game_over_flag = self.round_by_ocr(screen, '电玩店-蛇对蛇', area).is_fail
        # print('game_over_flag', game_over_flag)
        # area = self.ctx.screen_loader.get_area('电玩店-蛇对蛇', '游戏结束')
        # score_img = cv2_utils.crop_image_only(screen, area.rect)
        # score_str = self.ctx.ocr.run_ocr_single_line(score_img)
        # print(score_str)
        if ocr_result == '5':
            game_over_flag = False
        else:
            game_over_flag = True
        # print('game_over_flag', game_over_flag)

        # game_over_flag = True
        return game_over_flag        

