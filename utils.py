from openai import OpenAI
from dotenv import load_dotenv
import os
import wave
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_openai_response(messages):
    system_message = [{ "role": "system", "content": "You are a helpful AI chatbot, that answers questions asked by the User." }]
    prompt_message = system_message + messages

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt_message
    )               
    return response.choices[0].message.content

def speech_to_text(audio_binary):
    with open(audio_binary, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            response_format='text'
        )

    return transcript

def text_to_speech(text, voice='nova', pitch=1.0, speed=1.0):
    response = client.audio.speech.create(
        model='tts-1',
        input=text,
        voice=voice,
        pitch=pitch,
        speed=speed
    )   

    response_audio = '_output_audio.mp3'
    with open(response_audio, 'wb') as f:
        response.stream_to_file(response_audio)

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

def vad_filter(audio_file, silence_thresh=-40, min_silence_len=500):
    # Load the audio file
    audio = AudioSegment.from_file(audio_file)

    # Detect non-silent chunks
    nonsilent = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

    if nonsilent:
        # Concatenate all non-silent chunks
        non_silent_audio = AudioSegment.empty()
        for start, end in nonsilent:
            non_silent_audio += audio[start:end]

        # Export the non-silent audio to a new file
        vad_audio_file = 'vad_audio.mp3'
        non_silent_audio.export(vad_audio_file, format="mp3")

        return vad_audio_file

    return None
