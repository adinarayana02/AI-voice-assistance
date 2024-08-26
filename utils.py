import openai
import os
import numpy as np
import webrtcvad
import wave
import tempfile
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_openai_response(messages):
    """
    Get response from OpenAI API based on the messages.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error in get_openai_response: {e}")
        return "Sorry, I couldn't process your request."

def speech_to_text_with_vad(audio_file):
    """
    Convert speech to text using VAD to filter out silence.
    """
    try:
        vad_file = vad(audio_file)
        if vad_file:
            # Add your preferred speech-to-text processing here.
            # For demo purposes, we will assume a placeholder function.
            transcript = "Sample transcript from processed audio."
            return transcript
        else:
            return "No speech detected."
    except Exception as e:
        print(f"Error in speech_to_text_with_vad: {e}")
        return "Error processing speech."

def text_to_speech(text, voice):
    """
    Convert text to speech.
    """
    try:
        # Placeholder for text-to-speech conversion
        # Replace with your TTS implementation
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio_file.close()
        return audio_file.name
    except Exception as e:
        print(f"Error in text_to_speech: {e}")
        return None

def autoplay_audio(audio_file):
    """
    Play audio using pydub for demo purposes.
    """
    try:
        audio = AudioSegment.from_wav(audio_file)
        play(audio)
    except Exception as e:
        print(f"Error in autoplay_audio: {e}")

def vad(audio_file):
    """
    Apply Voice Activity Detection (VAD) to the audio file and save the processed audio.
    """
    try:
        vad = webrtcvad.Vad(1)  # Mode 1 is a trade-off between sensitivity and false positives

        with wave.open(audio_file, 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            audio_data = wf.readframes(wf.getnframes())

        print(f"Sample rate: {sample_rate}")
        print(f"Number of channels: {num_channels}")
        print(f"Sample width: {sampwidth}")

        if sampwidth != 2:
            raise ValueError("Audio sample width must be 2 bytes (16-bit PCM).")

        audio_np = np.frombuffer(audio_data, dtype=np.int16)

        frame_duration_ms = 30
        frame_size = int(sample_rate * frame_duration_ms / 1000)
        
        def frames_generator(audio_np, frame_size):
            """Generate frames of audio data."""
            for start in range(0, len(audio_np), frame_size):
                yield audio_np[start:start + frame_size]

        filtered_audio = bytearray()
        
        for frame in frames_generator(audio_np, frame_size):
            frame_bytes = frame.tobytes()
            if len(frame_bytes) == 0:
                continue
            try:
                if vad.is_speech(frame_bytes, sample_rate):
                    filtered_audio.extend(frame_bytes)
            except Exception as e:
                print(f"Error processing frame: {e}")

        vad_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        with wave.open(vad_file.name, 'wb') as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            wf.writeframes(filtered_audio)

        return vad_file.name
    except Exception as e:
        print(f"Error in vad function: {e}")
        return None
