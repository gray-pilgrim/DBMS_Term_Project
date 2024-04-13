import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
import numpy as np
import matplotlib.pyplot as plt
import spacy
from sklearn.metrics.pairwise import cosine_similarity

def load_model():
    # Load pre-trained VGG16 model without the top (fully connected) layers
    model_i2i = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model_t2t = spacy.load("en_core_web_md")
    return model_i2i, model_t2t
    # return model_i2i, None

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

def compute_semantic_similarity(nlp, text1, text2):
    # Compute word embeddings for each text
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    
    # Compute the average word embedding for each text
    embedding1 = doc1.vector.reshape(1, -1)
    embedding2 = doc2.vector.reshape(1, -1)
    
    # Compute cosine similarity between the embeddings
    cosine_sim = cosine_similarity(embedding1, embedding2)
    
    return cosine_sim[0][0]