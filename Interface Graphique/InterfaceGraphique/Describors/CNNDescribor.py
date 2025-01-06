import tensorflow as tf
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.applications.mobilenet import preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np

class CNNDescribor:
    def __init__(self):
        self.vector = None
        self.model = MobileNet(weights='imagenet', include_top=False, pooling='avg')

    def train_model(self, img_path):
        img = image.load_img(img_path, target_size=(448, 448))
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)

        self.vector = self.model.predict(img_data)
        return self.vector