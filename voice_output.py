import streamlit as st
from gtts import gTTS
import os
from datetime import datetime

# Generate speech
def generate_voice(input_text):
    if input_text.strip():
        try:
            # Convert text to Cantonese speech
            tts = gTTS(text=input_text, lang="yue", tld="com.hk")  # Specify Cantonese with Hong Kong accent

            # Get the current date and time
            now = datetime.now()
            # Format the date and time as a string
            timestamp = now.strftime("%Y%m%d_%H%M%S")  # Example: 20231225_153045
            # Create the file name
            audio_file = f"./speech/speech_{timestamp}.mp3"
            tts.save(audio_file)
            return audio_file

        except Exception as e:
            st.error(f"An error occurred: {e}")