import openai
import webrtcvad
import numpy as np
import wave
import tempfile
from gtts import gTTS
from io import BytesIO
import whisper
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_gpt4omini_response(prompt):
    # Make a request to the GPT-4o Mini model
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Ensure this is the correct model name for GPT-4o Mini
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def speech_to_text_with_vad(audio_file):
    # Use VAD to process audio
    vad_file = vad(audio_file)
    # Load Whisper model and transcribe
    model = whisper.load_model("base")
    result = model.transcribe(vad_file)
    return result['text']

def text_to_speech(text):
    tts = gTTS(text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tts_file.name)
    return tts_file.name

def autoplay_audio(file_path):
    st.audio(file_path, format='audio/mp3')

def vad(audio_file):
    vad = webrtcvad.Vad(1)
    audio, sample_rate = read_wave(audio_file)
    segments = vad_collector(sample_rate, 30, 300, vad, audio)
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
    save_wave(output_file, segments, sample_rate)
    return output_file

def read_wave(path):
    with wave.open(path, "rb") as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def save_wave(path, audio, sample_rate):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, audio):
    from collections import deque
    num_padding_frames = padding_duration_ms // frame_duration_ms
    ring_buffer = deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    for frame in frame_generator(frame_duration_ms, audio, sample_rate):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                voiced_frames.extend([f for f, speech in ring_buffer])
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])

def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], offset / n)
        offset += n

class Frame(object):
    def __init__(self, bytes, timestamp):
        self.bytes = bytes
        self.timestamp = timestamp
