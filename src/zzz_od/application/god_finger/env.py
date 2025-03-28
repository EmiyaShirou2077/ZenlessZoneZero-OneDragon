import numpy as np
import cv2
import time
from one_dragon.base.controller.pc_button.pc_button_controller import PcButtonController


class GreedySnakeEnv:
    def __init__(self, app):
        self.app = app  # full GodFingerApp
        self.ctx = app.ctx
        self.last_score = 0.0

        self.score_area_ratio = {
            "top": 0.05,
            "bottom": 0.11,
            "left": 0.395,
            "right": 0.74
        }

        self.game_area_ratio = {
            "top":  0.185,
            "bottom": 0.956,
            "left": 0.25,
            "right": 0.75
        }

        self.reset_area_ratio = {
            "top": 0.92,
            "bottom": 0.956,
            "left": 0.87,
            "right": 0.92
        }


    def reset(self):
        self.ctx.controller.btn_controller.press('j', press_time=0.1)
        time.sleep(3)
        self.last_score = 0.0
        obs = self._get_observation(self.app.screenshot())
        return obs

    def step(self, action: str):
        self._press_key(action)
        time.sleep(0.5)
        screen = self.app.screenshot()
        # check if game over
        flag_game_over = self._check_game_over(screen)
        if flag_game_over:
            return None, -1, True, {}
        
        game_img = self._get_observation(screen)
        score = self._get_score(screen)
        reward = self._get_reward(score)
        self.last_score = score

        return game_img, reward, flag_game_over, {}

    def _press_key(self, key: str):
        self.ctx.controller.btn_controller.press(key, press_time=0.1)

    def _get_score(self, screen):
        height, width = screen.shape[:2]
        top = int(height * self.score_area_ratio["top"])
        bottom = int(height * self.score_area_ratio["bottom"])
        left = int(width * self.score_area_ratio["left"])
        right = int(width * self.score_area_ratio["right"])
        score_img = screen[top:bottom, left:right]
        threshold_value = 180  # you can tune this
        _, score_img = cv2.threshold(score_img, threshold_value, 255, cv2.THRESH_BINARY)
        score_str = self.ctx.ocr.run_ocr_single_line(score_img)
        # print(f"score_str: {score_str}")
        if score_str == "":
            return self.last_score
        else:
            # remove space and convert to float
            score_str = score_str.replace(" ", "")
            score = float(score_str)
        return score

    def _get_observation(self, screen):
        height, width = screen.shape[:2]
        top = int(height * self.game_area_ratio["top"])
        bottom = int(height * self.game_area_ratio["bottom"]) 
        left = int(width * self.game_area_ratio["left"])
        right = int(width * self.game_area_ratio["right"])        
        game_img = screen[top:bottom, left:right]
        return game_img
    

    def _get_reward(self, current_score):

        reward = current_score - self.last_score
        if reward > 0:
            print(f"current_score: {current_score}, last_score: {self.last_score}")
            print(f"reward: {reward}")
        return reward

    def _check_game_over(self, screen):
        height, width = screen.shape[:2]
        top = int(height * self.reset_area_ratio["top"])
        bottom = int(height * self.reset_area_ratio["bottom"])
        left = int(width * self.reset_area_ratio["left"])
        right = int(width * self.reset_area_ratio["right"])
        reset_img = screen[top:bottom, left:right]
        reset_str = self.ctx.ocr.run_ocr_single_line(reset_img)
        print(f"reset_str: {reset_str}")
        # if reset_str == "再次挑战":
        if reset_str != "加速":
            return True
        else:
            return False

