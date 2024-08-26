import openai
import os
import webrtcvad
import numpy as np
import wave
import tempfile
from gtts import gTTS
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_gpt4omini_response(prompt):
    """
    Get a response from the GPT-4o Mini model.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Ensure this is the correct model name
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request."

def speech_to_text_with_vad(audio_file):
    """
    Convert speech to text using Whisper and apply Voice Activity Detection (VAD).
    """
    # Perform VAD
    vad_file = vad(audio_file)
    
    # Load Whisper model
    import whisper
    model = whisper.load_model("base")
    
    # Read and transcribe the audio
    result = model.transcribe(vad_file)
    return result['text']

def text_to_speech(text, voice='default'):
    """
    Convert text to speech with the specified voice.
    """
    tts = gTTS(text=text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tts_file.name)
    return tts_file.name

def autoplay_audio(file_path):
    """
    Play the audio file in Streamlit.
    """
    st.audio(file_path, format='audio/mp3')

def vad(audio_file):
    """
    Apply Voice Activity Detection (VAD) to the audio file.
    """
    # Initialize VAD
    vad = webrtcvad.Vad(1)
    
    # Read the audio file
    with wave.open(audio_file, 'rb') as wf:
        sample_rate = wf.getframerate()
        frame_duration = 30  # ms
        frames_per_buffer = int(sample_rate * frame_duration / 1000)
        audio_data = wf.readframes(wf.getnframes())
    
    # Apply VAD
    audio_bytes = bytearray(audio_data)
    filtered_audio = bytearray()
    
    for start in range(0, len(audio_bytes), frames_per_buffer):
        end = min(start + frames_per_buffer, len(audio_bytes))
        frame = audio_bytes[start:end]
        
        if vad.is_speech(frame, sample_rate):
            filtered_audio.extend(frame)
    
    # Save filtered audio
    vad_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with wave.open(vad_file.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(filtered_audio)
    
    return vad_file.name
