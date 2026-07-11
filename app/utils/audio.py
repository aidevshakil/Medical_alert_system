from pydub import AudioSegment
import numpy as np

def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    return audio

def preprocess_audio(audio):
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    return audio

def audio_to_numpy(audio):
    samples = np.array(audio.get_array_of_samples())
    return samples.astype(np.float32) / np.max(np.abs(samples))  # Normalize audio

def save_audio(audio, output_path):
    audio.export(output_path, format="wav")