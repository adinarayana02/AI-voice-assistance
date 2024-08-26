import openai
import webrtcvad
import numpy as np
import wave
import tempfile
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment

# Initialize OpenAI API (replace with your own API key)
openai.api_key = 'YOUR_OPENAI_API_KEY'

def get_gpt4omini_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4-omni",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def vad(audio_file):
    vad = webrtcvad.Vad(1)
    audio_data = AudioSegment.from_file(audio_file, format='wav').get_raw_data()
    sample_rate = 16000
    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000)
    frames = [audio_data[i:i + frame_size] for i in range(0, len(audio_data), frame_size)]
    voiced_frames = [frame for frame in frames if vad.is_speech(frame, sample_rate)]
    voiced_audio = b''.join(voiced_frames)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(voiced_audio)
        return temp_file.name

def speech_to_text_with_vad(audio_file):
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result['text']

def text_to_speech(text):
    tts = gTTS(text, lang='en')
    tts_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tts_file.name)
    return tts_file.name

def autoplay_audio(file_path):
    st.audio(file_path, format='audio/mp3')
