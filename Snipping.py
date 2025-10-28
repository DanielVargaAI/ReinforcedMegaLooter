import pyautogui
from PIL import Image
from Data import *
import os


def snip_slots(left, top, right, bottom, lib_img):
    # Schneide den Bereich aus dem Bild aus
    snipped_image = lib_img.crop((left, top, right, bottom))

    return snipped_image


def snip_library_slots():
    """Snip all library slots from all library images."""
    counter = 0
    # for all pages in the library images from folder Screenshots\Library
    for lib_name in os.listdir("Screenshots\\Library"):
        if lib_name.endswith(".png"):
            lib_img = Image.open(os.path.join("Screenshots\\Library", lib_name))
            for y in library[1]:
                for x in library[0]:
                    if lib_name.startswith("Page5"):
                        if library[1].index(y) < 3:
                            continue
                        if library[1].index(y) == 4:
                            if library[0].index(x) > 1:
                                continue
                        # Apply offset for page 5
                        snipped_slot = snip_slots(x[0], y[0]+27, x[1], y[1]+27, lib_img)
                    else:
                        snipped_slot = snip_slots(x[0], y[0], x[1], y[1], lib_img)
                    save_name = str("snipped_images\\snipped_slot_" + str(counter) + ".png")
                    snipped_slot.save(save_name)
                    counter += 1


if __name__ == "__main__":
    snip_library_slots()
