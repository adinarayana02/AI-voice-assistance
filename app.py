import streamlit as st
import asyncio
from utils import audio_to_text, get_llm_response, text_to_speech, restrict_output

st.title("Voice and Text AI Assistant")

# Section for Text Input
st.header("Enter Your Query")
text_query = st.text_area("Type your question here:", "")

# Section for Audio Input
st.header("Or Speak Your Query")
audio_file = st.file_uploader("Upload an audio file (WAV format only):", type=["wav"])

# Process Text Input
if text_query:
    st.subheader("Response")
    response_text = get_llm_response(text_query)
    st.write(restrict_output(response_text))
    
    # Convert text response to speech
    audio_file = asyncio.run(text_to_speech(response_text))
    st.audio(audio_file, format="audio/mp3")

# Process Audio Input
if audio_file:
    # Save uploaded audio to a temporary file
    with open("uploaded_audio.wav", "wb") as f:
        f.write(audio_file.read())

    st.subheader("Audio Processing")
    # Convert audio to text
    transcript = audio_to_text("uploaded_audio.wav")
    st.write("Transcript:", transcript)
    
    # Generate response from transcript
    response_text = get_llm_response(transcript)
    st.write(restrict_output(response_text))
    
    # Convert text response to speech
    audio_file = asyncio.run(text_to_speech(response_text))
    st.audio(audio_file, format="audio/mp3")
