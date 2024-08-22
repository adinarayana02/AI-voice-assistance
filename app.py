import streamlit as st
import os
from utils import get_openai_response, speech_to_text, text_to_speech, autoplay_audio
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

st.set_page_config(page_title="AI Voice Assistant", page_icon="🤖", layout="wide")

float_init()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

initialize_session_state()

st.title("Your Personal Voice Assistant 🤖")

voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    voice = st.selectbox(
        "Choose your preferred voice",
        ['Alloy', 'Echo', 'Fable', 'Onyx', 'Nova', 'Shimmer'],
        placeholder="Select a voice"
    ).lower()

footer = st.container()

prompt = st.chat_input("Enter your message here or click on the microphone to start recording")
with footer:
    audio = audio_recorder()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

if audio:
    with st.spinner("Transcribing audio..."):
        audio_file = 'temp_audio.mp3'
        try:
            with open(audio_file, 'wb') as f:
                f.write(audio)

            transcript = speech_to_text(audio_file)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)

if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = get_openai_response(st.session_state.messages)
            except Exception as e:
                st.error(f"Error getting response from OpenAI: {e}")
                response = "Sorry, I encountered an error while processing your request."

        with st.spinner("Generating response..."):
            try:
                response_audio = text_to_speech(response, voice)
                autoplay_audio(response_audio)
            except Exception as e:
                st.error(f"Error generating text-to-speech audio: {e}")
                response_audio = None

        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        if response_audio and os.path.exists(response_audio):
            os.remove(response_audio)
    
footer.float("bottom: -0.25rem;")
