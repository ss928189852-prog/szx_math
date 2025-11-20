import streamlit as st
from enhanced_voice_input import simple_voice_input, sidebar_voice_input, create_web_speech_input

st.set_page_config(
    page_title="Enhanced Voice Input Demo",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Enhanced Voice Input Demo")
st.markdown("### Real-time Cantonese Voice Input with Progressive Text Display")

# Add some styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.feature-card {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    background-color: #f9f9f9;
}

.recording-animation {
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎤 Enhanced Voice Input System</h1>
    <p>Real-time Cantonese speech recognition with progressive text display</p>
</div>
""", unsafe_allow_html=True)

# Demo sections
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📝 Method 1: Enhanced Streamlit Voice Input")
    st.markdown("""
    <div class="feature-card">
        <h4>Features:</h4>
        <ul>
            <li>🎯 Real-time transcription</li>
            <li>🎨 Beautiful UI with animations</li>
            <li>🇭🇰 Cantonese language support</li>
            <li>📱 Mobile-friendly design</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo the enhanced voice input
    st.markdown("#### Try it out:")
    voice_text = simple_voice_input("在此輸入或使用語音輸入", key="demo1")
    
    if voice_text:
        st.success(f"✅ 輸入的文字: {voice_text}")

with col2:
    st.markdown("### 🎤 Method 2: Sidebar Voice Input")
    st.markdown("""
    <div class="feature-card">
        <h4>Features:</h4>
        <ul>
            <li>📱 Optimized for sidebar</li>
            <li>🎯 Compact design</li>
            <li>🇭🇰 Cantonese language support</li>
            <li>⚡ No column restrictions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo the sidebar voice input
    st.markdown("#### Try it out:")
    sidebar_voice_text = sidebar_voice_input("側邊欄語音輸入", key="demo2")
    
    if sidebar_voice_text:
        st.success(f"✅ 側邊欄語音輸入: {sidebar_voice_text}")

# Add a third section for Web Speech API
st.markdown("---")
st.markdown("### 🌐 Method 3: Web Speech API (Browser-based)")
st.markdown("""
<div class="feature-card">
    <h4>Features:</h4>
    <ul>
        <li>⚡ Instant transcription</li>
        <li>🌍 Works in modern browsers</li>
        <li>🎤 No server-side processing</li>
        <li>📊 Real-time confidence scores</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Demo the web speech API
st.markdown("#### Try it out:")
web_voice_text = create_web_speech_input("使用瀏覽器語音輸入", key="demo3")

if web_voice_text:
    st.success(f"✅ 瀏覽器語音輸入: {web_voice_text}")

# Instructions
st.markdown("---")
st.markdown("### 📋 How to Use")

instructions = """
1. **Click the microphone button** 🎤 to start recording
2. **Speak clearly in Cantonese** - the system will transcribe your speech in real-time
3. **Watch the text appear** as you speak
4. **Click stop** when you're done recording
5. **Review and edit** the transcribed text if needed
6. **Submit** your response

**Tips for better accuracy:**
- Speak clearly and at a normal pace
- Minimize background noise
- Use a good quality microphone
- Speak in standard Cantonese pronunciation
"""

st.markdown(instructions)

# Technical details
with st.expander("🔧 Technical Details"):
    st.markdown("""
    ### Implementation Details
    
    **Method 1: Enhanced Streamlit Voice Input**
    - Uses `streamlit-mic-recorder` with custom UI enhancements
    - Real-time transcription with Google Speech Recognition
    - Cantonese language support (`yue-HK`)
    - Custom CSS animations and styling
    
    **Method 2: Web Speech API**
    - Browser-native speech recognition
    - No server-side processing required
    - Instant transcription with interim results
    - Works offline in modern browsers
    
    **Dependencies:**
    - `streamlit-mic-recorder==0.1.6`
    - `SpeechRecognition==3.10.0`
    - `PyAudio==0.2.11`
    
    **Language Support:**
    - Primary: Cantonese (Hong Kong) - `yue-HK`
    - Fallback: Chinese (Hong Kong) - `zh-HK`
    """)

# Usage examples
with st.expander("💡 Usage Examples"):
    st.markdown("""
    ### Example Phrases to Try
    
    **Mathematics:**
    - "五加三等於八"
    - "二分之一加三分之一"
    - "請幫我計算這個分數"
    
    **General Conversation:**
    - "你好，我想問一個問題"
    - "這個答案對不對？"
    - "可以解釋一下嗎？"
    
    **Questions:**
    - "我應該怎樣做這道題？"
    - "這個步驟對嗎？"
    - "為什麼要這樣計算？"
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🎤 Enhanced Voice Input System | Built with Streamlit</p>
    <p>Supporting Cantonese speech recognition with real-time transcription</p>
</div>
""", unsafe_allow_html=True) 