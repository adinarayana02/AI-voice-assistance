import openai
from dotenv import load_dotenv
import os
import base64
import streamlit as st

# Load environment variables
load_dotenv()

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(messages):
    system_message = [{ "role": "system", "content": "You are a helpful AI chatbot that answers questions asked by the user." }]
    prompt_message = system_message + messages

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=prompt_message
        )
        return response.choices[0].message['content']
    except openai.OpenAIError as e:
        st.error(f"Error getting response from OpenAI: {e}")
        return "Sorry, I couldn't generate a response."

def speech_to_text(audio_binary):
    try:
        with open(audio_binary, 'rb') as audio_file:
            transcript = openai.Audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
                response_format='text'
            )
        return transcript['text']
    except openai.OpenAIError as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def text_to_speech(text, voice='nova'):
    try:
        response = openai.Audio.speech.create(
            model='tts-1',
            input=text,
            voice=voice
        )   
        response_audio = '_output_audio.mp3'
        with open(response_audio, 'wb') as f:
            f.write(response['audio'])
        return response_audio
    except openai.OpenAIError as e:
        st.error(f"Error generating text-to-speech audio: {e}")
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
