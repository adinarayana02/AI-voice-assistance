import openai
import os
import streamlit as st
import base64

# Load the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(messages):
    try:
        # Prepare the request for OpenAI's GPT model
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )               
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process your request at the moment."

def speech_to_text(audio_binary):
    try:
        with open(audio_binary, 'rb') as audio_file:
            response = openai.Audio.create(
                model="whisper-1",
                file=audio_file,
                response_format='text'
            )
        return response['text']
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

def text_to_speech(text, voice='nova'):
    try:
        response = openai.Audio.create(
            model="text-to-speech",
            input=text,
            voice=voice
        )
        response_audio = '_output_audio.mp3'
        with open(response_audio, 'wb') as f:
            f.write(response['data'])
        
        return response_audio
    except Exception as e:
        st.error(f"Error generating speech: {e}")
        return None

def autoplay_audio(audio_file):
    try:
        if audio_file:
            with open(audio_file, 'rb') as audio_file_:
                audio_bytes = audio_file_.read()
            
            b64 = base64.b64encode(audio_bytes).decode("utf-8")
            md = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
            st.markdown(md, unsafe_allow_html=True)
        else:
            st.error("No audio file provided for playback.")
    except Exception as e:
        st.error(f"Error playing audio: {e}")
