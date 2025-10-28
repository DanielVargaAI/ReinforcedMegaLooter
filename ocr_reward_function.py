"""
Conceptual Python code for an RL environment wrapper with a
custom reward function based on in-game values (Floor, Enemy Count).

This version focuses on "reward shaping" rather than just end-of-episode detection.
"""

import cv2
import numpy as np
import pytesseract  # You will need this (and Tesseract-OCR)
                    # for the OCR method: pip install pytesseract
import re

class SlayTheSpireEnvWrapper:
    """
    A conceptual wrapper for your game environment.
    'self.env' would be the underlying game instance you are controlling.
    
    This wrapper reads game state (floor, enemy count) via OCR
    and calculates a reward based on the *change* in those values.
    """

    def __init__(self, env):
        self.env = env
        
        # --- For OCR ---
        # Define the screen regions (ROIs) for the values you want to read.
        # These are placeholder coordinates [y1:y2, x1:x2].
        # You MUST find these coordinates yourself (e.g., in an image editor).
        self.roi_floor = (50, 100, 200, 300)      # Example ROI for "1 | 100"
        self.roi_enemies = (50, 100, 700, 800)    # Example ROI for "4"
        
        # --- State Tracking ---
        # Store the values from the previous step to calculate deltas.
        self.prev_floor = 1
        self.prev_enemies = 0
        
        # --- Tesseract Config ---
        # Whitelist numbers. We removed the '|' as it's not essential.
        # --psm 7 treats the image as a single line of text.
        self.tesseract_config = r'--oem 0 --psm 7 -c tessedit_char_whitelist=0123456789'


    def _read_game_values(self, observation: np.ndarray) -> (int, int):
        """
        Reads the current floor and enemy count from the screen observation
        using OCR.
        """
        
        current_floor = self.prev_floor
        current_enemies = self.prev_enemies

        try:
            # --- Read Floor ---
            roi_f_img = observation[self.roi_floor[0]:self.roi_floor[1], self.roi_floor[2]:self.roi_floor[3]]
            floor_text = self._run_ocr(roi_f_img)
            
            # Use regex to find the first number (the floor count)
            # This is more robust in case the "| 100" part changes or disappears.
            match = re.search(r'(\d+)', floor_text)
            if match:
                current_floor = int(match.group(1))

            # --- Read Enemies ---
            roi_e_img = observation[self.roi_enemies[0]:self.roi_enemies[1], self.roi_enemies[2]:self.roi_enemies[3]]
            enemy_text = self._run_ocr(roi_e_img)
            
            # Use regex to find just the number
            match = re.search(r'(\d+)', enemy_text)
            if match:
                current_enemies = int(match.group(1))
                
        except Exception as e:
            print(f"Error in OCR: {e}. Using previous values.")
            # Return the last known good values if OCR fails
            return self.prev_floor, self.prev_enemies
        
        return current_floor, current_enemies

    def _run_ocr(self, image: np.ndarray) -> str:
        """Helper function to pre-process and run Tesseract."""
        # Pre-process for OCR: Grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Threshold to get white text on black background. Tune '150' as needed.
        _thresh, thresh_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Run OCR
        text = pytesseract.image_to_string(thresh_img, config=self.tesseract_config)
        return text.strip()

    def _check_for_done(self, info: dict) -> bool:
        """
        (Optional but recommended)
        Checks if the game environment is signaling 'done' via the info dict.
        """
        # Look for game state keys. These are just guesses;
        # you must inspect your environment's 'info' object.
        if info.get('game_state') == 'GAME_OVER':
            return True
        if info.get('player_health') == 0:
            return True
        return False


    def step(self, action):
        """
        This is the main function you would call from your RL loop.
        """
        # Get the standard outputs from the game
        observation, base_reward, env_done, info = self.env.step(action)
        
        # Read the values from the screen
        current_floor, current_enemies = self._read_game_values(observation)

        # --- Reward Shaping Logic ---
        reward = 0.0
        
        # 1. Small penalty for every step taken to encourage speed
        reward -= 0.01 

        # 2. Large positive reward for advancing to a new floor
        if current_floor > self.prev_floor:
            reward += 10.0
            print(f"REWARD: Advanced to floor {current_floor}! (+10.0)")

        # 3. Positive reward for defeating an enemy
        if current_enemies < self.prev_enemies:
            enemies_defeated = self.prev_enemies - current_enemies
            reward += (enemies_defeated * 1.0) # 1.0 reward per enemy
            print(f"REWARD: Defeated {enemies_defeated} enemy! (+{enemies_defeated * 1.0})")
        
        # --- Update State for Next Step ---
        self.prev_floor = current_floor
        self.prev_enemies = current_enemies

        # --- Check for Episode End ---
        # Check if the game's info dict says we died or won
        is_done = self._check_for_done(info) or env_done

        if is_done and info.get('player_health', 1) == 0:
            # If we died, apply a large negative reward
            reward = -20.0
            print("PENALTY: Agent died. (-20.0)")
        
        # The final reward is the sum of the base env reward + our shaped reward
        final_reward = base_reward + reward

        return observation, final_reward, is_done, info

    def reset(self):
        """
        Resets the environment for a new episode.
        """
        # Reset the underlying environment
        observation = self.env.reset()
        
        # Read the *initial* values from the screen after reset
        try:
            self.prev_floor, self.prev_enemies = self._read_game_values(observation)
            print(f"Environment reset. Starting at Floor: {self.prev_floor}, Enemies: {self.prev_enemies}")
        except Exception as e:
            print(f"Error reading initial state on reset: {e}")
            self.prev_floor = 1
            self.prev_enemies = 0 # Guess a default
        
        return observation
        


