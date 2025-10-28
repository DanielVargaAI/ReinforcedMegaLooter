"""
Standalone OCR module for reading game values (Floor, Enemy Count)
from a game screen observation.

This code is extracted from the larger RL wrapper.
"""

import cv2
import numpy as np
import pytesseract  # You will need this (and Tesseract-OCR)
                    # for the OCR method: pip install pytesseract
import re


class GameValueReader:
    """
    Reads specific game values from a screen observation (numpy array)
    using OCR (Tesseract).
    """

    def __init__(self):
        # --- For OCR ---
        # Define the screen regions (ROIs) for the values you want to read.
        # These are placeholder coordinates [y1:y2, x1:x2].
        # You MUST find these coordinates yourself (e.g., in an image editor).

        # 578, 31  - 916, 67
        self.roi_floor = (578, 916, 31, 67)      # Example ROI for "1"
        self.roi_enemies = (578, 31, 916, 67)    # Example ROI for "4"
        
        # --- Tesseract Config ---
        # Whitelist numbers.
        # --psm 7 treats the image as a single line of text.
        self.tesseract_config = r'--oem 0 --psm 7 -c tessedit_char_whitelist=0123456789'

    def _run_ocr(self, image: np.ndarray) -> str:
        """Helper function to pre-process and run Tesseract."""
        # Pre-process for OCR: Grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Threshold to get white text on black background. Tune '150' as needed.
        _thresh, thresh_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Run OCR
        text = pytesseract.image_to_string(thresh_img, config=self.tesseract_config)
        return text.strip()

    def read_game_values(self, observation: np.ndarray) -> (int | None, int | None):
        """
        Reads the current floor and enemy count from the screen observation
        using OCR.
        
        Returns (current_floor, current_enemies).
        Values can be None if OCR fails to read them.
        """
        
        current_floor = None
        current_enemies = None

        try:
            # --- Read Floor ---
            roi_f_img = observation[self.roi_floor[0]:self.roi_floor[1], self.roi_floor[2]:self.roi_floor[3]]

            print(observation)

            floor_text = self._run_ocr(roi_f_img)
            
            # Use regex to find the first number (the floor count)
            match_floor = re.search(r'(\d+)', floor_text)
            if match_floor:
                current_floor = int(match_floor.group(1))

            # --- Read Enemies ---
            roi_e_img = observation[self.roi_enemies[0]:self.roi_enemies[1], self.roi_enemies[2]:self.roi_enemies[3]]
            enemy_text = self._run_ocr(roi_e_img)
            
            # Use regex to find just the number
            match_enemy = re.search(r'(\d+)', enemy_text)
            if match_enemy:
                current_enemies = int(match_enemy.group(1))
                
        except Exception as e:
            print(f"Error in OCR: {e}. Returning None for failed values.")
            # Return None for values that failed
            return current_floor, current_enemies
        
        return current_floor, current_enemies


# --- Example Usage (if you were to run this file) ---
if __name__ == "__main__":
    # Create a dummy observation image (e.g., 800x600, 3 channels)
    # In your real code, this 'dummy_screen' would come from your env.
    # dummy_screen = np.zeros((800, 600, 3), dtype=np.uint8)

    # open Screen.png and use it as dummy_screen
    dummy_screen = cv2.imread("Screen.png")

    # You would need to paste your game screenshot data here
    # For example, pretend 'dummy_screen' is your game capture.
    
    # Initialize the reader
    reader = GameValueReader()
    
    # IMPORTANT: You must update reader.roi_floor and reader.roi_enemies
    # with the correct pixel coordinates for your game screen.
    # reader.roi_floor = (y1, y2, x1, x2)
    # reader.roi_enemies = (y1, y2, x1, x2)

    print("--- Example OCR Run ---")
    print(f"Using Floor ROI: {reader.roi_floor}")
    print(f"Using Enemies ROI: {reader.roi_enemies}")
    
    # This will likely fail on a black screen, but shows how to call it:
    floor, enemies = reader.read_game_values(dummy_screen)
    
    print(f"\nOCR Result:")
    print(f"Floor read: {floor}")
    print(f"Enemies read: {enemies}")
    print("\nRemember to set the correct ROI coordinates in the class!")
