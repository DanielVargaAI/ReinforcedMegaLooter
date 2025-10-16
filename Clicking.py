import pyautogui
from Data import *


def click_button(button):
    """Move the mouse to (x, y) and perform a click."""
    x, y = MousePositions[button]
    pyautogui.moveTo(x, y)
    pyautogui.click()


click_button("Equipment1")
