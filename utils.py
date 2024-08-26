import openai
import webrtcvad
import numpy as np
import wave
import tempfile
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API (use the environment variable)
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_openai_response(messages):
    """
    Get a response from the OpenAI API using GPT-4-OMini.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-omni",  # Ensure this is the correct model name for GPT-4-OMini
        messages=messages
    )
    return response['choices'][0]['message']['content']

def speech_to_text_with_vad(audio_file):
    """
    Convert speech to text using Whisper and apply Voice Activity Detection (VAD).
    """
    # Apply VAD to the audio file
    vad_file = vad(audio_file)
    
    # Load Whisper model
    import whisper
    model = whisper.load_model("base")
    
    # Read and transcribe the audio
    result = model.transcribe(vad_file)
    return result['text']

def text_to_speech(text, voice):
    """
    Convert text to speech using gTTS and return the path to the saved audio file.
    """
    tts = gTTS(text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tts_file.name)
    return tts_file.name

def autoplay_audio(file_path):
    """
    Play audio file in Streamlit.
    """
    st.audio(file_path, format='audio/mp3')

def vad(audio_file):
    """
    Apply Voice Activity Detection (VAD) to the audio file and save the processed audio.
    """
    # Initialize VAD
    vad = webrtcvad.Vad(1)
    
    # Read the audio file
    with wave.open(audio_file, 'rb') as wf:
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        audio_data = wf.readframes(wf.getnframes())
    
    # Convert audio data to a format suitable for VAD
    frame_duration = 30  # ms
    frames_per_buffer = int(sample_rate * frame_duration / 1000)
    
    def frames_generator(audio_data, frame_duration, sample_rate):
        num_channels = 1  # Assuming mono audio
        frame_size = int(sample_rate * frame_duration / 1000 * num_channels * sampwidth)
        for start in range(0, len(audio_data), frame_size):
            end = min(start + frame_size, len(audio_data))
            yield audio_data[start:end]

    filtered_audio = bytearray()
    
    for frame in frames_generator(audio_data, frame_duration, sample_rate):
        if vad.is_speech(frame, sample_rate):
            filtered_audio.extend(frame)
    
    # Save filtered audio
    vad_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with wave.open(vad_file.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sample_rate)
        wf.writeframes(filtered_audio)
    
    return vad_file.name
