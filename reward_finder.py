"""
read out text from specific regions of the screen using easyOCR
"""
import cv2
import easyocr

# Load the image
image_path = "Screenshots/InGame/InGame_61.png"
image = cv2.imread(image_path)

# Define the ROI (x1, y1, x2, y2)
roi = (575, 30, 915, 70)

# Crop the image to the ROI
x1, y1, x2, y2 = roi
cropped_image = image[y1:y2, x1:x2]

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])  # Specify the language(s)

# Perform OCR on the cropped image
result = reader.readtext(cropped_image, allowlist='0123456789', text_threshold=0.4)

# Print the detected text
for detection in result:
    text = detection[1]  # Extract the text from the result
    print(f"Detected text: {text}")
