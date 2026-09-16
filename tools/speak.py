import subprocess
import sounddevice as sd
import soundfile as sf
import os
import uuid
from tools.clean_text_for_speech import clean_text_for_speech

VOICE_MODEL = "voices/en_US-hfc_female-medium.onnx"
AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def speak(text: str):
    clean_text = clean_text_for_speech(text)
    if not clean_text or len(clean_text.strip()) < 2:
        return

    output_path = os.path.join(AUDIO_DIR, f"output_{uuid.uuid4().hex[:8]}.wav")
    result = subprocess.run(
        ["piper", "--model", VOICE_MODEL, "--output_file", output_path],
        input=clean_text.encode("utf-8"),
        capture_output=True,
    )

    if result.returncode != 0:
        print("Piper failed:")
        print("STDOUT:", result.stdout.decode(errors="replace"))
        print("STDERR:", result.stderr.decode(errors="replace"))
        return

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
        return

    data, samplerate = sf.read(output_path)
    sd.play(data, samplerate)
    sd.wait()