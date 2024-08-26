import streamlit as st
import io
from utils import get_llm_response, audio_to_text, text_to_speech, restrict_output
import asyncio

# Streamlit app
st.title("Voice and Text AI Assistant")

# Audio input section
st.header("Voice Input")
audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

if st.button("Record Audio"):
    st.write("Please record your audio below.")
    # Use `st.audio` to capture audio input from microphone if available

# Text input section
st.header("Text Input")
user_input = st.text_area("Enter your query here")

if st.button("Submit"):
    # Handle audio file input
    if audio_file is not None:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.read())
        # Convert audio to text
        query_text = audio_to_text("temp_audio.wav")
    else:
        query_text = user_input
    
    # Restrict the response to 2 sentences
    query_text = restrict_output(query_text)
    
    # Get response from LLM
    response_text = get_llm_response(query_text)
    
    # Restrict response text to 2 sentences
    response_text = restrict_output(response_text)
    
    # Convert text to speech
    async def generate_speech():
        audio_file = await text_to_speech(response_text)
        return audio_file
    
    audio_file_path = asyncio.run(generate_speech())
    
    # Display response
    st.subheader("AI Response")
    st.write(response_text)
    
    # Play audio response
    with open(audio_file_path, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")
