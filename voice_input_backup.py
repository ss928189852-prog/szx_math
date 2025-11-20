import streamlit as st
import speech_recognition as sr
import time


def record_voice(language):
    """
    Continuous voice recognition using Google Speech Recognition
    Recognizes speech in real-time and updates text input progressively
    """
    # Language mapping for Google Speech Recognition
    language_mapping = {
        "yue_hk": "zh-HK",  # Cantonese (Hong Kong)
        "zh": "zh-TW",      # Traditional Chinese
        "zh-cn": "zh-CN",   # Simplified Chinese
        "en": "en-US"       # English
    }
    
    # Get the appropriate language code
    google_language = language_mapping.get(language, "zh-HK")
    
    # Initialize recording state
    if "is_recording" not in st.session_state:
        st.session_state["is_recording"] = False
    if "recorded_text" not in st.session_state:
        st.session_state["recorded_text"] = ""
    
    # Create a toggle button for recording
    button_text = "⏹️" if st.session_state["is_recording"] else "🎤"
    button_help = "按此停止語音輸入" if st.session_state["is_recording"] else "按此開始語音輸入"
    
    record_button = st.button(
        button_text,
        key="record_button",
        help=button_help,
        use_container_width=True
    )
    
    # Handle button click
    if record_button:
        st.session_state["is_recording"] = not st.session_state["is_recording"]
        if st.session_state["is_recording"]:
            st.session_state["recorded_text"] = ""
        st.rerun()
    
    # Show recording status and handle continuous recognition
    if st.session_state["is_recording"]:
        status_placeholder = st.empty()
        
        def show_status(message, color="blue"):
            """Helper function to show status messages"""
            colors = {
                "blue": "#e7f3ff",
                "green": "#e8f5e8", 
                "red": "#ffebee"
            }
            borders = {
                "blue": "#2196F3",
                "green": "#4caf50",
                "red": "#f44336"
            }
            status_placeholder.markdown(f"""
            <div style="background-color: {colors[color]}; border: 1px solid {borders[color]}; border-radius: 4px; padding: 10px; margin: 10px 0 10px -160px; text-align: left;">
                {message}
            </div>
            """, unsafe_allow_html=True)
        
        show_status("🎤 請說話 (按 ⏹️ 停止)", "blue")
        
        try:
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Use microphone as source
            with sr.Microphone() as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Continuous recognition loop
                while st.session_state["is_recording"]:
                    try:
                        # Listen for speech with very short timeout
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        # Try to recognize the speech
                        text = None
                        for lang in [google_language, "zh"]:
                            try:
                                text = recognizer.recognize_google(audio, language=lang)
                                break
                            except sr.UnknownValueError:
                                continue
                            except sr.RequestError as e:
                                show_status(f"❌ 服務錯誤: {str(e)}", "red")
                                st.session_state["is_recording"] = False
                                return None
                        
                        if text:
                            # Append to recorded text
                            if st.session_state["recorded_text"]:
                                st.session_state["recorded_text"] += " " + text
                            else:
                                st.session_state["recorded_text"] = text
                            
                            # Update the text input immediately
                            st.session_state["voice_transcribed_text"] = st.session_state["recorded_text"]
                            st.session_state["input_counter"] = st.session_state.get("input_counter", 0) + 1
                            
                            # Show current accumulated text
                            show_status(f"✅ {st.session_state['recorded_text']}", "green")
                            
                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        continue
                    except Exception as e:
                        show_status(f"❌ 錄音錯誤: {str(e)}", "red")
                        st.session_state["is_recording"] = False
                        break
                
                # Recognition stopped
                if st.session_state["recorded_text"]:
                    show_status(f"✅ 語音識別完成: {st.session_state['recorded_text']}", "green")
                else:
                    show_status("❌ 沒有識別到語音", "red")
                
                time.sleep(2)
                status_placeholder.empty()
                
        except Exception as e:
            st.session_state["is_recording"] = False
            show_status(f"❌ 錄音錯誤: {str(e)}", "red")
            time.sleep(2)
            status_placeholder.empty()
    
    return None


def get_microphone_info():
    """Get information about available microphones"""
    try:
        return sr.Microphone.list_microphone_names()
    except Exception as e:
        return [f"Error getting microphones: {e}"]


def debug_microphone():
    """Debug function to test microphone settings"""
    st.write("### 麥克風偵測")
    microphones = get_microphone_info()
    st.write("可用麥克風:")
    for i, mic in enumerate(microphones):
        st.write(f"  {i}: {mic}")
    
    # Test microphone access
    if st.button("測試麥克風"):
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("正在測試麥克風...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                st.success("✅ 麥克風測試成功!")
        except Exception as e:
            st.error(f"❌ 麥克風測試失敗: {e}")

