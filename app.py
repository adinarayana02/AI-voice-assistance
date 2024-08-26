import streamlit as st
import os
from utils import get_openai_response, speech_to_text_with_vad, text_to_speech_with_params, autoplay_audio, limit_response_to_two_sentences
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

# UI for selecting voice parameters
voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    voice = st.selectbox(
        "Choose your preferred voice",
        ['Alloy', 'Echo', 'Fable', 'Onyx', 'Nova', 'Shimmer'],
        placeholder="Select a voice"
    ).lower()

    pitch = st.slider("Pitch", -10, 10, 0)
    speed = st.slider("Speed", 0.5, 2.0, 1.0)

footer = st.container()

# User input and recording audio
prompt = st.chat_input("Enter your message here or click on the microphone to start recording")
with footer:
    audio = audio_recorder()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Process text input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Process audio input
if audio:
    with st.spinner("Processing audio..."):
        audio_file = 'temp_audio.mp3'
        with open(audio_file, 'wb') as f:
            f.write(audio)

        transcript = speech_to_text_with_vad(audio_file)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(audio_file)

# Generate and display response
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = get_openai_response(st.session_state.messages)
            response = limit_response_to_two_sentences(response)

        with st.spinner("Generating audio..."):
            response_audio = text_to_speech_with_params(response, voice, pitch, speed)
            if response_audio:
                autoplay_audio(response_audio)

        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        os.remove(response_audio)

footer.float("bottom: -0.25rem;")
