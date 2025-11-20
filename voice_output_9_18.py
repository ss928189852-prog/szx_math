import streamlit as st
from gtts import gTTS
import os
import io
from datetime import datetime

# Generate speech
def generate_voice(input_text):
    if input_text.strip():
        try:
            # Convert text to Cantonese speech
            tts = gTTS(text=input_text, lang="yue", tld="com.hk")  # Specify Cantonese with Hong Kong accent
            # Save to a BytesIO object
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)  # Reset the buffer position
            return audio_buffer

        except Exception as e:
            st.error(f"An error occurred: {e}")
