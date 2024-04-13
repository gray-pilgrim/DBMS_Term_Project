import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
import numpy as np
import matplotlib.pyplot as plt

import os
import IPython
import matplotlib
import requests
import torch
import torchaudio


def load_model():
    # Load pre-trained VGG16 model without the top (fully connected) layers
    model_i2i = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    return model_i2i

def load_and_preprocess_image(image_path, target_size=(224, 224)):
    img = image.load_img(image_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def compute_image_similarity(model, image_path1, image_path2):
    # Load and preprocess images
    img1 = load_and_preprocess_image(image_path1)
    img2 = load_and_preprocess_image(image_path2)

    # Get feature vectors from VGG16 model
    features1 = model.predict(img1)
    features2 = model.predict(img2)

    # Flatten the feature vectors
    features1 = features1.flatten()
    features2 = features2.flatten()

    # Compute cosine similarity
    dot_product = np.dot(features1, features2)
    norm1 = np.linalg.norm(features1)
    norm2 = np.linalg.norm(features2)
    similarity = dot_product / (norm1 * norm2)

    return similarity

class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, blank=0):
        super().__init__()
        self.labels = labels
        self.blank = blank

    def forward(self, emission: torch.Tensor) -> str:
        """Given a sequence emission over labels, get the best path string
        Args:
        emission (Tensor): Logit tensors. Shape `[num_seq, num_label]`.
        Returns:
        str: The resulting transcript
        """
        indices = torch.argmax(emission, dim=-1) # [num_seq,]
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i != self.blank]
        return "".join([self.labels[i] for i in indices])
