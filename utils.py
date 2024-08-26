import openai
import os
import base64
from gtts import gTTS
from pydub import AudioSegment
import io
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

def speech_to_text(audio_file):
    try:
        with open(audio_file, 'rb') as file:
            transcript = openai.Audio.transcriptions.create(
                model='whisper-1',
                file=file,
                response_format='text'
            )
        return transcript['text']
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, I couldn't transcribe the audio."

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = 'output_audio.mp3'
        tts.save(audio_file)
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
