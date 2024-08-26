import openai
import webrtcvad
import numpy as np
import wave
import whisper
import tempfile
from gtts import gTTS
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_openai_response(messages):
    """
    Get response from GPT-4 using OpenAI API.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Ensure this is the correct model name for GPT-4-OMini
        messages=messages
    )
    return response['choices'][0]['message']['content']

def speech_to_text_with_vad(audio_file):
    """
    Convert speech to text using VAD and Whisper.
    """
    vad_file = vad(audio_file)
    # Assume VAD processing returns a valid WAV file path
    
    model = whisper.load_model("base")
    result = model.transcribe(vad_file)
    return result['text']

def text_to_speech(text, voice='default'):
    """
    Convert text to speech.
    """
    tts = gTTS(text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tts_file.name)
    return tts_file.name

def autoplay_audio(file_path):
    """
    Play the audio file.
    """
    st.audio(file_path, format='audio/mp3')

def vad(audio_file):
    """
    Apply Voice Activity Detection (VAD) to the audio file and save the processed audio.
    """
    # Initialize VAD
    vad = webrtcvad.Vad(1)  # Mode 1 is a trade-off between sensitivity and false positives
    
    # Read the audio file
    with wave.open(audio_file, 'rb') as wf:
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        audio_data = wf.readframes(wf.getnframes())
    
    # Ensure audio data is in 16-bit PCM format
    if sampwidth != 2:
        raise ValueError("Audio sample width must be 2 bytes (16-bit PCM).")

    # Convert audio data to a numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    
    # Define frame duration and calculate frame size
    frame_duration_ms = 30
    frame_size = int(sample_rate * frame_duration_ms / 1000)
    
    def frames_generator(audio_np, frame_size):
        """Generate frames of audio data."""
        for start in range(0, len(audio_np), frame_size):
            yield audio_np[start:start + frame_size]

    filtered_audio = bytearray()
    
    for frame in frames_generator(audio_np, frame_size):
        if vad.is_speech(frame.tobytes(), sample_rate):
            filtered_audio.extend(frame.tobytes())
    
    # Save filtered audio
    vad_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with wave.open(vad_file.name, 'wb') as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(filtered_audio)
    
    return vad_file.name
