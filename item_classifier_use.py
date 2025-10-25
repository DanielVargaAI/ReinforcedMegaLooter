# To use the model for prediction, load it with:
# model = tf.keras.models.load_model("item_classifier_model.h5")
# and then call model.predict() on new images.
# Example prediction:
# test_img = Image.open("snipped_images/snipped_slot_0.png").resize(image_size)
# test_img_array = (np.array(test_img) / 255.0) * 2 - 1
# test_img_array = np.expand_dims(test_img_array, axis=0)  # Add batch dimension
# predictions = model.predict(test_img_array)
# predicted_class = np.argmax(predictions, axis=1)
import tensorflow as tf
from PIL import Image
import numpy as np
import os


def classify_item(image_path):
    # Load the trained model
    model = tf.keras.models.load_model("item_classifier_model.h5")
    # Load and preprocess the image
    img = Image.open(image_path).resize((100, 100))
    img_array = (np.array(img) / 255.0) * 2 - 1
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    # Make prediction
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)
    return predicted_class


if __name__ == "__main__":
    test_images_path = "Screenshots\\test"
    # test all images in the folder
    for img_name in os.listdir(test_images_path):
        if img_name.endswith(".png"):
            img_path = os.path.join(test_images_path, img_name)
            predicted_class = classify_item(img_path)
            print(f"Image: {img_name}, Predicted Class: {predicted_class[0]}")
