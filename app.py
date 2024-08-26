import streamlit as st
import os
import base64
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from utils import get_openai_response, speech_to_text, text_to_speech, autoplay_audio

# Load environment variables from .env file
load_dotenv()

# Set the page configuration
st.set_page_config(page_title="AI Voice Assistant", page_icon="🤖", layout="wide")

# Function to initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

initialize_session_state()

# Page title
st.title("Your Personal Voice Assistant 🤖")

# Layout for voice selection
voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    voice = st.selectbox(
        "Choose your preferred voice",
        ['Alloy', 'Echo', 'Fable', 'Onyx', 'Nova', 'Shimmer'],
        placeholder="Select a voice"
    ).lower()

footer = st.container()

# User input for text or audio
prompt = None
prompt = st.chat_input("Enter your message here or click on the microphone to start recording")
with footer:
    audio = audio_recorder()

# Display previous messages
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
        audio_file = 'temp_audio.mp3'
        with open(audio_file, 'wb') as f:
            f.write(audio)

        transcript = speech_to_text(audio_file)
        if transcript:
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.write(transcript)
            os.remove(audio_file)

# Generate and display response
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_openai_response(st.session_state.messages)

        with st.spinner("Generating response..."):
            response_audio = text_to_speech(response, voice)
            autoplay_audio(response_audio)

        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        os.remove(response_audio)

# Footer configuration
footer.float("bottom: -0.25rem;")
