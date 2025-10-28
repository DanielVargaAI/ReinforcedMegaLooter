"""
gymnasium environment setup for a custom reinforcement learning task.
This module defines a custom environment by subclassing gymnasium.Env
"""
import cv2
import gymnasium as gym
from easyocr import easyocr
from gymnasium import spaces
import numpy as np
import pyautogui
from simple_settings import *
import keyboard
import sys


def perform_reset():
    # Perform any necessary actions to reset the game
    pyautogui.moveTo(1610, 940)
    pyautogui.click()
    pyautogui.sleep(1)
    pyautogui.click()
    pyautogui.sleep(1)


class CustomEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # === Action Space ===
        # (x, y, click_type)
        # x, y ∈ [0,1], click_type ∈ [0,3)
        self.action_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0]),
            high=np.array([1.0, 1.0, 2.99]),
            dtype=np.float32
        )

        # === Observation Space ===
        # Wir skalieren den Screenshot auf TODO 640x360
        self.screen_width = 1920
        self.screen_height = 1080
        self.obs_width = scale_to_x
        self.obs_height = scale_to_y
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(3, self.obs_height, self.obs_width),
            dtype=np.uint8
        )

        # === State Tracking ===
        self.current_screen = None
        self.current_stage = 0
        self.new_current_stage = 0
        self.stage_started_at = 0
        self.current_battles_left = 0
        self.new_current_battles_left = 0
        self.current_rewards = []
        self.turn_counter = 0

        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'])  # Specify the language(s)

    def reset(self, seed=None, options=None):
        # Reset the state of the environment to an initial state
        super().reset(seed=seed)
        self.get_screenshot()
        self.read_current_progression_state()
        self.update_current_progression_state()
        self.stage_started_at = self.current_stage
        self.current_rewards = []
        self.turn_counter = 0
        return self.current_screen, {}

    def step(self, action):
        # Perform the action in the environment
        self.perform_action(action)

        # wait 0.5 seconds to give the game time to resolve the action
        pyautogui.sleep(0.5)

        # Execute one time step within the environment
        self.get_screenshot()
        self.read_current_progression_state()
        observation = self.current_screen
        reward = self.get_reward()
        terminated = self.check_termination()
        if terminated:
            perform_reset()
        truncated = self.check_truncation()
        if truncated:
            print("[INFO] Episode truncated due to soft reset condition.")
        info = {}
        if keyboard.is_pressed('f10'):
            sys.exit("Manual exit requested.")
        self.turn_counter += 1
        return observation, reward, terminated, truncated, info

    def perform_action(self, action):
        # action = {"mouse": np.array([x, y]), "click": int}
        x = 45 + float(action[0]) * 1770  # max at 1815
        y = 90 + float(action[1]) * 955  # max at 1045
        click_type = int(np.round(action[2]))

        pyautogui.moveTo(x, y)

        if click_type == 0:
            pyautogui.click()
        elif click_type == 1:
            pyautogui.click(button='right')
        elif click_type == 2:
            pyautogui.press('s')
        elif click_type == 3:
            # no action (e.g., hover over an item)
            pass

    def get_info(self):
        # TODO: return any additional info
        pass

    def check_termination(self):
        # Load the main image and template
        image = np.transpose(self.current_screen, (1, 2, 0))
        template = cv2.imread("Screenshots\\snipped_confirm_button.png")

        # Convert images to grayscale
        image_gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # Find locations where the matching result exceeds the threshold
        threshold = 0.8
        locations = np.where(result >= threshold)

        return len(locations[0]) > 0  # Return True if any match found

    def check_truncation(self):
        # return True if more than 3 stages have been passed without termination (soft reset)
        if self.new_current_stage - self.stage_started_at >= 3:
            return True
        elif self.turn_counter >= 60:  # ~300 seconds
            return True
        else:
            return False

    def get_reward(self):
        # first simple reward function based on stage and progression
        new_reward = -1  # default negative reward to encourage faster completion

        if self.new_current_stage > self.current_stage:
            new_reward += 100  # reward for advancing a stage
        elif self.new_current_battles_left < self.current_battles_left:
            new_reward += 80  # slightly smaller reward for winning a battle in the same stage

        if self.check_termination():
            new_reward -= 50  # penalty for reaching termination state (died)

        self.update_current_progression_state()

        # log the reward
        self.current_rewards.append(new_reward)
        return new_reward

    def render(self, mode='human'):
        # Render the environment to the screen
        # likely not needed, as we should see the game screen
        pass

    def close(self):
        # Clean up resources
        # likely not needed
        pass

    def get_screenshot(self):
        screen = pyautogui.screenshot()
        screen = np.array(screen)
        # scale down
        screen = cv2.resize(screen, (self.obs_width, self.obs_height))
        # switch to (C, H, W)
        screen = np.transpose(screen, (2, 0, 1))
        self.current_screen = screen

    def read_current_progression_state(self):
        # image should be the image from self.current_screen
        image = pyautogui.screenshot()
        image = np.array(image)

        # Define the ROI (x1, y1, x2, y2)
        roi = (575, 30, 915, 70)

        # # scale ROI to current observation size
        # x_scale = self.obs_width / self.screen_width
        # y_scale = self.obs_height / self.screen_height
        # roi = (int(roi[0] * x_scale), int(roi[1] * y_scale), int(roi[2] * x_scale), int(roi[3] * y_scale))

        # Crop the image to the ROI
        x1, y1, x2, y2 = roi
        cropped_image = image[y1:y2, x1:x2]

        # Perform OCR on the cropped image
        result = self.reader.readtext(cropped_image, allowlist='0123456789', text_threshold=0.4)
        progression_texts = [x[1] for x in result]

        # Extract stage and battles left
        self.new_current_stage = int(progression_texts[0]) if progression_texts else 0
        self.new_current_battles_left = int(progression_texts[-1]) if len(progression_texts) > 1 else 0

    def update_current_progression_state(self):
        # update the current stage and battles left
        self.current_stage = self.new_current_stage
        self.current_battles_left = self.new_current_battles_left


if __name__ == "__main__":
    env = CustomEnv()
    obs, info = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    action = env.action_space.sample()
    obs, reward, done, truncated, info = env.step(action)
    print(f"Step observation shape: {obs.shape}, Reward: {reward}, Done: {done}")
    env.close()
