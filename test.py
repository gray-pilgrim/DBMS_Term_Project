import os
import IPython
import matplotlib
import matplotlib.pyplot as plt
import requests
import torch
import torchaudio


from moviepy.editor import VideoFileClip

# Load the video file
# video = VideoFileClip("video.mp4")

# # Extract the audio from the video
# audio = video.audio

# # Write the audio to a file
# audio.write_audiofile("audio.mp3")


# SPEECH_URL = "https://keithito.com/LJ-Speech-Dataset/LJ025-0076.wav"
# SPEECH_FILE = "_assets/speech.wav"
# if not os.path.exists(SPEECH_FILE):
#     os.makedirs("_assets", exist_ok=True)
#     with open(SPEECH_FILE, "wb") as file:
#         file.write(requests.get(SPEECH_URL).content)

# SPEECH_URL = "https://drive.google.com/drive/folders/1pULxmgec4d0avJjg8iydvCgFeW2UB-34?usp=drive_link"
# SPEECH_FILE = "harvard.wav"


# SPEECH_FILE = "harvard.wav"
SPEECH_FILE = "greet.mp3"
# if not os.path.exists(SPEECH_FILE):
    # os.makedirs("_assets", exist_ok=True)
    # with open(SPEECH_FILE, "wb") as file:
    #     file.write(requests.get(SPEECH_URL).content)


IPython.display.Audio(SPEECH_FILE)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device {device}")
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
print(f"Sample Rate: {bundle.sample_rate}")
print(f"Labels: {bundle.get_labels()}")
model = bundle.get_model().to(device)
print(model.__class__)

# waveform, sample_rate = torchaudio.load(SPEECH_FILE)
waveform, sample_rate = torchaudio.load(SPEECH_FILE, format="mp3")
# waveform, sample_rate = torchaudio.load(SPEECH_FILE)
waveform = waveform.to(device)
if sample_rate != bundle.sample_rate:
    waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)


with torch.inference_mode():
    emission, _ = model(waveform)

plt.imshow(emission[0].cpu().T)
plt.title("Classification result")
plt.xlabel("Frame (time-axis)")
plt.ylabel("Class")
plt.show()
print("Class labels:", bundle.get_labels())



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


decoder = GreedyCTCDecoder(labels=bundle.get_labels())
transcript = decoder(emission[0])


print(transcript)
