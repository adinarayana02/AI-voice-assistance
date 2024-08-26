import streamlit as st
import os
from utils import get_gpt4omini_response, speech_to_text_with_vad, text_to_speech, autoplay_audio
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

prompt = None
prompt = st.chat_input("Enter your message here or click on the microphone to start recording")
with footer:
    audio = audio_recorder()

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle text input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Handle audio input
if audio:
    with st.spinner("Transcribing audio..."):
        audio_file = 'temp_audio.wav'
        with open(audio_file, 'wb') as f:
            f.write(audio)

        transcript = speech_to_text_with_vad(audio_file)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(audio_file)

# Generate response and text-to-speech output
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_gpt4omini_response(st.session_state.messages[-1]["content"])
            st.write(response)

            # Generate speech audio from response
            response_audio = text_to_speech(response, voice)
            st.write("Text-to-Speech Output:")
            autoplay_audio(response_audio)

            # Update chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            os.remove(response_audio)

footer.float("bottom: -0.25rem;")
