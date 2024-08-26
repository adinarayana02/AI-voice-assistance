import openai
import os
from gtts import gTTS
import webrtcvad
from pydub import AudioSegment
from pydub.silence import split_on_silence
import base64
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Set API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message["content"]
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request."

def speech_to_text_with_vad(audio_file):
    vad = webrtcvad.Vad(2)  # Aggressiveness mode
    try:
        audio = AudioSegment.from_file(audio_file, format="mp3")
        chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-30)

        transcript = ""
        for chunk in chunks:
            raw_audio = chunk.raw_data
            if vad.is_speech(raw_audio, sample_rate=16000):
                with open("temp_chunk.mp3", "wb") as f:
                    f.write(raw_audio)
                with open("temp_chunk.mp3", 'rb') as file:
                    result = openai.Audio.transcriptions.create(
                        model='whisper-1',
                        file=file,
                        response_format='text'
                    )
                    transcript += result['text'] + " "
        return transcript.strip()
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't transcribe the audio."

def limit_response_to_two_sentences(response):
    return '. '.join(response.split('. ')[:2]) + '.'

def text_to_speech_with_params(text, voice, pitch, speed):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = 'output_audio.mp3'
        tts.save(audio_file)

        # Adjust pitch and speed using pydub
        audio = AudioSegment.from_file(audio_file)
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
        audio = audio.set_frame_rate(44100)
        
        if pitch != 0:
            octaves = pitch / 10.0
            new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(44100)
        
        audio.export(audio_file, format="mp3")
        return audio_file
    except Exception as e:
        print(f"Error in text-to-speech conversion: {e}")
        return None

def autoplay_audio(audio_file):
    try:
        with open(audio_file, 'rb') as audio_file_:
            audio_bytes = audio_file_.read()

        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        md = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error in autoplaying audio: {e}")
