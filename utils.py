import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(messages):
    system_message = [{"role": "system", "content": "You are a helpful AI chatbot that answers questions asked by the User."}]
    prompt_message = system_message + messages

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt_message
    )
    
    return response.choices[0].message['content']

def speech_to_text(audio_binary):
    with open(audio_binary, 'rb') as audio_file:
        transcript = openai.Audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='text'
        )
    
    return transcript['text']

def text_to_speech(text, voice='nova'):
    response = openai.Audio.speech.create(
        model='tts-1',
        input=text,
        voice=voice
    )
    
    response_audio = '_output_audio.mp3'
    with open(response_audio, 'wb') as f:
        f.write(response['audio'])
        
    return response_audio

def autoplay_audio(audio_file):
    with open(audio_file, 'rb') as audio_file_:
        audio_bytes = audio_file_.read()
    
    b64 = base64.b64encode(audio_bytes).decode("utf-8")
    md = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    return md
