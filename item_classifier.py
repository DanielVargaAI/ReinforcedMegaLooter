"""
CNN model for classifying items into multiple categories using TensorFlow and Keras.
items are classified into 191 categories based on their type.
items to classify are 100x100 pixel images in RGB format.
items are stored in snipped_images/ folder as snipped_slot_0.png, snipped_slot_1.png, ...
item labels are stored in item_labels.json as a dictionary mapping image index to item type.
"""
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from PIL import Image
# Load item labels
with open("item_mapper.json", "r") as f:
    item_labels = json.load(f)
num_classes = 191  # Number of item categories
image_size = (100, 100)  # Size of the input images
# Load images and labels
images = []
labels = []
for filename in os.listdir("snipped_images"):
    if filename.endswith(".png"):
        index = int(filename[13:-4])
        if str(index) in item_labels:
            img_path = os.path.join("snipped_images", filename)
            img = Image.open(img_path).resize(image_size)
            img_array = (np.array(img) / 255.0) * 2 - 1  # Normalize to [-1, 1]
            images.append(img_array)
            labels.append(item_labels[str(index)]["type"])

images = np.array(images)
labels = np.array(labels)

# Split into training and validation sets
# make sure, that each class is represented in both sets
X_train, X_val, y_train, y_val = train_test_split(
    images, labels, test_size=1/9, stratify=labels, random_state=42)

# Data generators
train_datagen = ImageDataGenerator()
val_datagen = ImageDataGenerator()
train_generator = train_datagen.flow(X_train, y_train, batch_size=32)
val_generator = val_datagen.flow(X_val, y_val, batch_size=32)

# Build the CNN model
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 4)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dense(num_classes, activation='softmax')
])
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(train_generator, epochs=50, validation_data=val_generator)
# Save the trained model
model.save("item_classifier_model.h5")
print("Model trained and saved as item_classifier_model.h5")

# create a crosstable of predicted vs actual labels on the validation set
val_predictions = model.predict(X_val)
val_pred_labels = np.argmax(val_predictions, axis=1)
# if predicted label != actual label, print both to a txt-file
with open("validation_misclassifications.txt", "w") as f:
    for actual, predicted in zip(y_val, val_pred_labels):
        if actual != predicted:
            f.write(f"Actual: {actual}, Predicted: {predicted}\n")
print("Validation misclassifications saved to validation_misclassifications.txt")

# To use the model for prediction, load it with:
# model = tf.keras.models.load_model("item_classifier_model.h5")
# and then call model.predict() on new images.
# Example prediction:
# test_img = Image.open("snipped_images/snipped_slot_0.png").resize(image_size)
# test_img_array = (np.array(test_img) / 255.0) * 2 - 1
# test_img_array = np.expand_dims(test_img_array, axis=0)  # Add batch dimension
# predictions = model.predict(test_img_array)
# predicted_class = np.argmax(predictions, axis=1)

