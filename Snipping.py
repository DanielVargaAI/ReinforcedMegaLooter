import pyautogui
from PIL import Image
from Data import *


def snip_slots(left, top, right, bottom, picture):
    # Schneide den Bereich aus dem Bild aus
    snipped_image = picture.crop((left, top, right, bottom))

    return snipped_image


if __name__ == "__main__":
    # Picture ist LibraryTest.png
    picture = Image.open("LibraryTest.png")
    counter = 0
    for x in library[0]:
        for y in library[1]:
            snipped_image = snip_slots(x[0], y[0], x[1], y[1], picture)
            save_name = str("snipped_images\\snipped_slot_" + str(counter) + ".png")
            snipped_image.save(save_name)
            counter += 1
