import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
import numpy as np
import matplotlib.pyplot as plt
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import os
import IPython
import matplotlib
import matplotlib.pyplot as plt
import requests
import torch
import torchaudio
from moviepy.editor import VideoFileClip

##################################################
## import packages
##################################################

from transformers import GPT2TokenizerFast, ViTImageProcessor, VisionEncoderDecoderModel
from torch.utils.data import Dataset
from torchtext.data import get_tokenizer
import requests
import torch
import numpy as np
from PIL import Image
import pickle
# from torchvision import transforms
# from datasets import load_dataset
# import torch.nn as nn
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')


def load_model():
    # Load pre-trained VGG16 model without the top (fully connected) layers
    model_i2i = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    # model_t2t = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model_t2t = spacy.load("en_core_web_md")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device {device}")
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    print(f"Sample Rate: {bundle.sample_rate}")
    print(f"Labels: {bundle.get_labels()}")
    model = bundle.get_model().to(device)

    model_a2t = [device, bundle, model]

    # model_raw = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    # image_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    # tokenizer       = GPT2TokenizerFast.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    # model_i2t = [model_raw, image_processor, tokenizer]
    model_i2t = None
    print("Im 2 text model loaded")

    return model_i2i, model_t2t, model_a2t, model_i2t
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

def text_from_audio(model_a2t, audio_path):
    SPEECH_FILE = audio_path
    # waveform, sample_rate = torchaudio.load(SPEECH_FILE)
    waveform, sample_rate = torchaudio.load(SPEECH_FILE, format="mp3")
    # waveform, sample_rate = torchaudio.load(SPEECH_FILE)
    waveform = waveform.to(model_a2t[0])
    if sample_rate != model_a2t[1].sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, model_a2t[1].sample_rate)


    with torch.inference_mode():
        emission, _ = model_a2t[2](waveform)

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


    decoder = GreedyCTCDecoder(labels=model_a2t[1].get_labels())
    transcript = decoder(emission[0])

    transcript = str(transcript).lower()
    transcript = transcript.split("|")
    transcript = " ".join(transcript)

    return transcript

def text_from_video(model_a2t, video_path):
    # Load the video file
    video = VideoFileClip(video_path)

    # # Extract the audio from the video
    audio = video.audio

    # # Write the audio to a file
    audio.write_audiofile("audio.mp3")

    SPEECH_FILE = "audio.mp3"
    # waveform, sample_rate = torchaudio.load(SPEECH_FILE)
    waveform, sample_rate = torchaudio.load(SPEECH_FILE, format="mp3")
    # waveform, sample_rate = torchaudio.load(SPEECH_FILE)
    waveform = waveform.to(model_a2t[0])
    if sample_rate != model_a2t[1].sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, model_a2t[1].sample_rate)


    with torch.inference_mode():
        emission, _ = model_a2t[2](waveform)

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


    decoder = GreedyCTCDecoder(labels=model_a2t[1].get_labels())
    transcript = decoder(emission[0])

    transcript = str(transcript).lower()
    transcript = transcript.split("|")
    transcript = " ".join(transcript)

    return transcript

def text_from_image(model_i2t, path, greedy=True):
    image = Image.open(path)
    pixel_values   = model_i2t[1](image, return_tensors ="pt").pixel_values
    # plt.imshow(np.asarray(image))
    # plt.show()

    if greedy:
        generated_ids  = model_i2t[0].generate(pixel_values, max_new_tokens = 30)
    else:
        generated_ids  = model_i2t[0].generate(
            pixel_values,
            do_sample=True,
            max_new_tokens = 30,
            top_k=5)
    generated_text = model_i2t[2].batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text