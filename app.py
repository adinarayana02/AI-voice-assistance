import streamlit as st
import os
import tempfile
from utils import get_gpt4omini_response, speech_to_text_with_vad, text_to_speech, autoplay_audio, vad

def main():
    st.title("AI Voice Assistance with GPT-4-OMini")

    # Upload audio file section
    st.header("Upload Audio")
    audio_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])

    if audio_file:
        st.audio(audio_file, format='audio/wav')
        if st.button("Process Audio"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_file.read())
                st.write("Processing audio file...")
                # Perform VAD
                vad_file = vad(temp_file.name)
                st.write("Voice Activity Detection complete.")
                st.audio(vad_file, format='audio/wav')
                st.write("Speech-to-Text:")
                transcript = speech_to_text_with_vad(vad_file)
                st.write(transcript)

                st.write("Chat with GPT-4-OMini:")
                user_query = st.text_input("Your query:", "")
                if user_query:
                    response = get_gpt4omini_response(user_query)
                    st.write(response)
                    tts_file = text_to_speech(response)
                    st.write("Text-to-Speech Output:")
                    autoplay_audio(tts_file)

    # Microphone recording section
    st.header("Record Audio")
    st.write("Click the button below to start recording your voice.")
    record_button = st.button("Record Audio")

    if record_button:
        st.write("Recording completed. Please upload your recorded audio file.")

    # Display recorded audio section
    st.header("Recorded Audio Playback")
    recorded_audio_file = st.file_uploader("Upload your recorded audio file", type=["wav", "mp3"])

    if recorded_audio_file:
        st.audio(recorded_audio_file, format='audio/wav')
        if st.button("Process Recorded Audio"):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(recorded_audio_file.read())
                st.write("Processing recorded audio file...")
                # Perform VAD
                vad_file = vad(temp_file.name)
                st.write("Voice Activity Detection complete.")
                st.audio(vad_file, format='audio/wav')
                st.write("Speech-to-Text:")
                transcript = speech_to_text_with_vad(vad_file)
                st.write(transcript)

                st.write("Chat with GPT-4-OMini:")
                user_query = st.text_input("Your query:", "")
                if user_query:
                    response = get_gpt4omini_response(user_query)
                    st.write(response)
                    tts_file = text_to_speech(response)
                    st.write("Text-to-Speech Output:")
                    autoplay_audio(tts_file)

if __name__ == "__main__":
    main()
