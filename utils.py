import whisper
import numpy as np
import wave
import webrtcvad
import openai
import io
from pydub import AudioSegment
import edge_tts
import os

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to read WAV file
def read_wav(file_path):
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        samp_width = wf.getsampwidth()
        n_frames = wf.getnframes()
        audio = wf.readframes(n_frames)
        return np.frombuffer(audio, dtype=np.int16), sample_rate

# Function to perform VAD
def vad(audio, sample_rate, vad_mode=1):
    vad = webrtcvad.Vad(vad_mode)
    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000)
    frames = [audio[i:i + frame_size] for i in range(0, len(audio), frame_size)]
    return [frame for frame in frames if vad.is_speech(frame, sample_rate)]

# Convert audio to text using Whisper
def audio_to_text(audio_path):
    model = whisper.load_model("base")  # Load Whisper model
    audio, sample_rate = read_wav(audio_path)
    audio = np.array(vad(audio, sample_rate))
    audio_wav = io.BytesIO()
    audio_segment = AudioSegment(
        audio.tobytes(), 
        frame_rate=sample_rate, 
        sample_width=2, 
        channels=1
    )
    audio_segment.export(audio_wav, format="wav")
    audio_wav.seek(0)
    result = model.transcribe(audio_wav, fp16=False)
    return result['text']

# Get response from OpenAI's GPT-4o-mini model
def get_llm_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message['content']

# Convert text to speech using Edge TTS
async def text_to_speech(text, voice='en-US-JennyNeural', pitch='0%', speed='1.0'):
    communicator = edge_tts.Communicate()
    output_file = "output.mp3"
    await communicator.synthesize(text, voice, pitch, speed, output_file)
    return output_file

# Restrict the output to 2 sentences
def restrict_output(response_text):
    sentences = response_text.split('. ')
    return '. '.join(sentences[:2]) + ('.' if sentences else '')
