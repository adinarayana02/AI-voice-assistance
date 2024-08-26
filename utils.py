import streamlit as st
import os
import base64
import openai
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

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

# Function to get response from OpenAI
def get_openai_response(messages):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by the User."}]
    prompt_message = system_message + messages

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt_message
    )
    
    return response.choices[0].message['content']

# Function to transcribe speech to text
def speech_to_text(audio_binary):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    with open(audio_binary, 'rb') as audio_file:
        transcript = openai.Audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='text'
        )
    
    return transcript['text']

# Function to convert text to speech
def text_to_speech(text, voice='nova'):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Audio.speech.create(
        model='tts-1',
        input=text,
        voice=voice
    )
    
    response_audio = '_output_audio.mp3'
    with open(response_audio, 'wb') as f:
        f.write(response['audio'])
        
    return response_audio

# Function to autoplay audio in the Streamlit app
def autoplay_audio(audio_file):
    with open(audio_file, 'rb') as audio_file_:
        audio_bytes = audio_file_.read()
    
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    md = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
