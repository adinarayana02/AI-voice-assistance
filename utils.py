import openai
import os
from dotenv import load_dotenv
import base64

load_dotenv()

# Set API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(messages):
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by User."}]
    prompt_message = system_message + messages

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=prompt_message
    )
    return response.choices[0].message["content"]

def speech_to_text(audio_binary):
    with open(audio_binary, 'rb') as audio_file:
        transcript = openai.Audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='text'
        )
    return transcript['text']

def text_to_speech(text, voice='nova'):
    response = openai.Audio.create(
        model='text-to-speech-1',
        input=text,
        voice=voice
    )
    response_audio = 'output_audio.mp3'
    with open(response_audio, 'wb') as f:
        f.write(response['data'])
    
    return response_audio

def autoplay_audio(audio_file):
    with open(audio_file, 'rb') as audio_file_:
        audio_bytes = audio_file_.read()

    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    md = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
