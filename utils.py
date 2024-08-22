import openai
import os
from dotenv import load_dotenv
import base64
import streamlit as st

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def get_openai_response(messages):
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot, that answers questions asked by the user."}]
    prompt_message = system_message + messages

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Adjust to your preferred model
        messages=prompt_message
    )
    return response.choices[0].message["content"]

def speech_to_text(audio_binary):
    try:
        with open(audio_binary, 'rb') as audio_file:
            transcript = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1"  # Adjust model as needed
            )
        return transcript['text']
    except openai.error.OpenAIError as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def text_to_speech(text, voice='nova'):
    response = openai.Audio.create(
        model='tts-1',
        input=text,
        voice=voice
    )   

    response_audio = '_output_audio.mp3'
    with open(response_audio, 'wb') as f:
        response.stream_to_file(response_audio)

    return response_audio

def autoplay_audio(audio_file):
    with open(audio_file, 'rb') as audio_file_:
        audio_bytes = audio_file_.read()

    b64 = base64.b64encode(audio_bytes).decode("utf-8")    
    md = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
