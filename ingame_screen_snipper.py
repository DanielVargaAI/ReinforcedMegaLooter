"""
snip_ingame_slots(path):
open image "MitItems.png", snip all equipment, shop and inventory slots and save them in folder "Sceenshots\test"

screenshot_ingame():
When started, makes a screenshot of the ingame screen and saves it with an ongoing index in folder "Screenshots\InGame"
makes a screenshot when F10 is pressed
"""
import os
from PIL import Image
from Data import *
import pyautogui
import keyboard
import time


def snip_ingame_slots(path):
    """Snip all test slots from image MitItems.png."""
    counter = 0
    inv_screen = Image.open(path)
    for key, value in Buttons.items():
        slot_img = inv_screen.crop((value[0][0], value[0][1], value[1][0], value[1][1]))
        save_name = str("Screenshots\\test\\snipped_slot_" + key + ".png")
        slot_img.save(save_name)
        counter += 1


def screenshot_ingame():
    """Take a screenshot of the ingame screen when F10 is pressed."""

    screenshot_folder = "Screenshots\\InGame"
    if not os.path.exists(screenshot_folder):
        os.makedirs(screenshot_folder)

    print("Press F10 to take a screenshot of the ingame screen. Press ESC to exit.")
    screenshot_counter = 0

    while True:
        if keyboard.is_pressed('f10'):
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(screenshot_folder, f"InGame_{screenshot_counter}.png")
            screenshot.save(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            screenshot_counter += 1
            time.sleep(1)  # Prevent multiple screenshots on a single press
        elif keyboard.is_pressed('esc'):
            print("Exiting screenshot mode.")
            break


if __name__ == "__main__":
    # screenshot_path = "Screenshots\\InGame\\MitItems.png"
    # snip_ingame_slots(screenshot_path)

    screenshot_ingame()
