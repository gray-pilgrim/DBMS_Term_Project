import numpy as np
from PIL import Image
from skimage.feature import graycomatrix, graycoprops
from sklearn.neighbors import KDTree
import librosa
import os

# Function to extract features from an image
def extract_features(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img_array = np.array(img)
        
        # 1. Calculate average color as feature
        average_color = np.mean(img_array, axis=(0, 1))
        
        # 2. Calculate color histogram as feature
        color_histogram = np.histogram(img_array.reshape(-1, 3), bins=256, range=[0, 256])[0]
        
        # 3. Calculate texture features using GLCM
        gray_image = img.convert("L")
        gray_array = np.array(gray_image)
        glcm = graycomatrix(gray_array, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], symmetric=True, normed=True)
        contrast = graycoprops(glcm, 'contrast').ravel()
        correlation = graycoprops(glcm, 'correlation').ravel()
        texture_features = np.concatenate([contrast, correlation])
        
        # Combine all features
        combined_features = np.concatenate([average_color, color_histogram, texture_features])
        
    return combined_features

# Function to extract MFCC features from audio
def extract_features_audio(audio_path, sr=22050, n_mfcc=13):
    # Load audio file
    y, sr = librosa.load(audio_path, sr=sr)
    
    # Extract MFCC features
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    
    # Flatten the MFCC matrix into a feature vector
    mfccs_flattened = np.mean(mfccs, axis=1)
    
    return mfccs_flattened



def most_similar_audio(need_paths, query_path):
    # Directory containing the images

    # List to store image paths and corresponding features
    image_paths = need_paths
    features = []

    # Loop through the images directory to extract features from each image
    for image_path in need_paths:
        feature = extract_features_audio(image_path)
        features.append(feature)

    # Convert features list to numpy array
    features_array = np.array(features)

    # Build the KD-tree
    kd_tree = KDTree(features_array)

    # Select a random image as the query image
    query_image_path = query_path
    query_feature = extract_features_audio(query_image_path)

    # Number of nearest neighbors to find
    k = 1

    # Search for the nearest neighbors to the query feature
    distances, indices = kd_tree.query([query_feature], k=k)

    return image_paths[indices[0][0]]

def most_similar(need_paths, query_path):
    # Directory containing the images

    # List to store image paths and corresponding features
    image_paths = need_paths
    features = []

    # Loop through the images directory to extract features from each image
    for image_path in need_paths:
        feature = extract_features(image_path)
        features.append(feature)

    # Convert features list to numpy array
    features_array = np.array(features)

    # Build the KD-tree
    kd_tree = KDTree(features_array)

    # Select a random image as the query image
    query_image_path = query_path
    query_feature = extract_features(query_image_path)

    # Number of nearest neighbors to find
    k = 1

    # Search for the nearest neighbors to the query feature
    distances, indices = kd_tree.query([query_feature], k=k)

    return image_paths[indices[0][0]]


