import openai
from dotenv import load_dotenv
import os
import base64
import streamlit as st

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def get_openai_response(messages):
    try:
        system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by users."}]
        prompt_message = system_message + messages

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt_message
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        st.error(f"Error getting response: {e}")
        return "Sorry, I couldn't process your request."

def speech_to_text(audio_binary):
    try:
        with open(audio_binary, 'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", file=audio_file)
        return transcript['text']
    except openai.error.OpenAIError as e:
        st.error(f"Error transcribing audio: {e}")
        return None
    except AttributeError as e:
        st.error(f"AttributeError: {e}")
        return None

def text_to_speech(text, voice='nova'):
    try:
        response = openai.Audio.create(
            model='tts-1',
            input=text,
            voice=voice
        )
        response_audio = '_output_audio.mp3'
        with open(response_audio, 'wb') as f:
            f.write(response['audio'])
        return response_audio
    except openai.error.OpenAIError as e:
        st.error(f"Error generating speech: {e}")
        return None

def autoplay_audio(audio_file):
    try:
        with open(audio_file, 'rb') as audio_file_:
            audio_bytes = audio_file_.read()
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        md = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error playing audio: {e}")
