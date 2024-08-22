import streamlit as st
import os
from utils import get_openai_response, speech_to_text, text_to_speech, autoplay_audio
from audio_recorder_streamlit import audio_recorder
from streamlit_float import *

# Set up the page
st.set_page_config(page_title="AI Voice Assistant", page_icon="🤖", layout="wide")

# Initialize floating footer
float_init()

# Function to initialize session state
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! How may I assist you today?"}
        ]

# Call the session state initialization function
initialize_session_state()

# Set the title of the app
st.title("Your Personal Voice Assistant 🤖")

# Voice selection and audio input columns
voice_col1, voice_col2 = st.columns([1, 2])
with voice_col1:
    voice = st.selectbox(
        "Choose your preferred voice",
        ['Alloy', 'Echo', 'Fable', 'Onyx', 'Nova', 'Shimmer'],
        placeholder="Select a voice"
        ).lower()

# Footer container for the floating effect
footer = st.container()

# Chat input for text messages
prompt = st.chat_input("Enter your message here or click on the microphone to start recording")

# Audio recording
with footer:
    audio = audio_recorder()

# Display previous chat messages
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
        try:
            with open(audio_file, 'wb') as f:
                f.write(audio)
            transcript = speech_to_text(audio_file)
            if transcript:
                st.session_state.messages.append({"role": "user", "content": transcript})
                with st.chat_message("user"):
                    st.write(transcript)
        except Exception as e:
            st.error(f"Error handling audio: {e}")
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)

# Generate assistant's response if the last message is from the user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = get_openai_response(st.session_state.messages)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                # Convert response to speech and play it
                with st.spinner("Generating response..."):
                    response_audio = text_to_speech(response, voice)
                    autoplay_audio(response_audio)
            except Exception as e:
                st.error(f"Error generating response: {e}")

# Add the floating footer effect
footer.float("bottom: -0.25rem;")
