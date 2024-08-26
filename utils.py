import os
import openai
import whisper
from pydub import AudioSegment
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Whisper model
whisper_model = whisper.load_model("base")

# Initialize Hugging Face LLM model
llm_pipeline = pipeline("text-generation", model="llama-13b")  # Example model, replace as needed

def speech_to_text_with_vad(audio_file):
    # Convert audio file to the correct format if needed
    audio = AudioSegment.from_file(audio_file, format="wav")
    audio = audio.set_channels(1).set_frame_rate(16000)  # Ensure mono and 16 kHz

    # Use Whisper model to transcribe the audio
    result = whisper_model.transcribe(audio_file, language="en")
    transcript = result['text']

    # Optional: Implement VAD logic to process transcript
    return transcript

def get_llm_response(messages):
    # Extract the latest user message
    user_message = messages[-1]["content"]

    # Generate a response using the LLM
    response = llm_pipeline(user_message, max_length=50, do_sample=True)[0]['generated_text']

    # Limit the response to 2 sentences
    sentences = response.split('.')
    response = '.'.join(sentences[:2]) + '.'
    return response

def text_to_speech(text, voice_type, pitch, speed):
    # Using a TTS model to generate speech
    from pyttsx3 import init

    tts_engine = init()
    tts_engine.setProperty('rate', speed * 100)  # Speed
    tts_engine.setProperty('pitch', pitch)  # Pitch, if supported

    # Choose voice based on user selection
    voices = tts_engine.getProperty('voices')
    if voice_type == 'male':
        tts_engine.setProperty('voice', voices[0].id)  # Example, adjust as necessary
    else:
        tts_engine.setProperty('voice', voices[1].id)  # Example, adjust as necessary

    # Generate and save speech audio
    audio_file = 'response.wav'
    tts_engine.save_to_file(text, audio_file)
    tts_engine.runAndWait()

    return audio_file

def autoplay_audio(file_path):
    # Function to play audio in Streamlit (if needed)
    import streamlit as st
    st.audio(file_path, format='audio/wav')
