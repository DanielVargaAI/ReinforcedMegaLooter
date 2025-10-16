import cv2
import numpy as np
import matplotlib.pyplot as plt

# === 1. Screenshot laden ===
# (du kannst hier auch einen Screenshot mit pyautogui oder mss aufnehmen)
img_path = "Screen.png"
img = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV lädt standardmäßig in BGR

# === 2. Farbwert definieren ===
# Beispiel: du hast den Rahmenfarbwert (R, G, B) manuell mit einem Bildeditor ermittelt
target_color = (47, 49, 59)  # Beispielwert, bitte anpassen

# === 3. Toleranz einstellen ===
# Kleine Abweichung erlaubt, da Screenshots minimale Farbunterschiede haben können
tolerance = 5  # je höher, desto mehr Pixel werden gefunden

# === 4. Maske erzeugen: Pixel vergleichen ===
lower = np.array([max(c - tolerance, 0) for c in target_color])
upper = np.array([min(c + tolerance, 255) for c in target_color])

# Maske: alle Pixel, die innerhalb des Farbbereichs liegen
mask = cv2.inRange(img_rgb, lower, upper)

# === 5. Koordinaten aller passenden Pixel extrahieren ===
coords = np.column_stack(np.where(mask > 0))
# np.where liefert (y, x) → wir vertauschen zu (x, y)
coords = [(int(x), int(y)) for y, x in coords]

print(f"{len(coords)} Pixel gefunden.")

# === 6. Plotten der Trefferpositionen ===
plt.figure(figsize=(8, 6))
plt.imshow(img_rgb)
if coords:
    xs, ys = zip(*coords)
    plt.scatter(xs, ys, s=3, c='red', label='Gefundene Pixel')
plt.legend()
plt.title("Gefundene Rahmenpixel")
plt.show()
