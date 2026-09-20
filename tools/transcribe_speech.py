import sounddevice as sd
import soundfile as sf
import os
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def record_audio(duration=5, samplerate=16000, filename="input.wav"):
    print("Listening...")
    audio_path = os.path.join(AUDIO_DIR, filename)
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(audio_path, audio, samplerate)
    return audio_path

def transcribe_speech(duration=5) -> str:
    audio_path = record_audio(duration=duration)
    segments, _ = model.transcribe(audio_path, language="en")
    text = " ".join(segment.text for segment in segments)
    return text.strip()