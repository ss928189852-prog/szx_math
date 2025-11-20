# 🎤 Enhanced Voice Input System

A real-time Cantonese voice input system for Streamlit applications with progressive text display and beautiful UI.

## ✨ Features

- **Real-time Transcription**: See your speech converted to text as you speak
- **Cantonese Language Support**: Optimized for Cantonese (Hong Kong) speech recognition
- **Beautiful UI**: Animated microphone button with recording indicators
- **Progressive Display**: Text appears in the input box as you speak
- **Multiple Methods**: Choose between Streamlit-based or browser-native speech recognition
- **Mobile-Friendly**: Responsive design that works on all devices

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```python
import streamlit as st
from enhanced_voice_input import simple_voice_input

# Create a voice input widget
voice_text = simple_voice_input("輸入文字", key="my_voice_input")

if voice_text:
    st.write(f"You said: {voice_text}")
```

### 3. Integration with Chatbot

The voice input is already integrated into the main chatbot. Users can:

1. Click the microphone button 🎤
2. Speak in Cantonese
3. Watch the text appear in real-time
4. Edit the text if needed
5. Submit their response

## 🎯 How It Works

### Method 1: Enhanced Streamlit Voice Input

```python
from enhanced_voice_input import simple_voice_input

# Creates a beautiful voice input widget
voice_text = simple_voice_input(
    placeholder_text="在此輸入或使用語音輸入",
    key="unique_key"
)
```

**Features:**
- Uses `streamlit-mic-recorder` with custom UI enhancements
- Real-time transcription with Google Speech Recognition
- Cantonese language support (`yue-HK`)
- Custom CSS animations and styling

### Method 2: Web Speech API (Browser-based)

```python
from enhanced_voice_input import create_web_speech_input

# Creates a browser-native voice input
voice_text = create_web_speech_input(
    placeholder_text="使用瀏覽器語音輸入",
    key="web_speech"
)
```

**Features:**
- Browser-native speech recognition
- No server-side processing required
- Instant transcription with interim results
- Works offline in modern browsers

## 🎨 UI Components

### Voice Input Widget

The voice input widget includes:

- **Microphone Button**: Large, animated button that changes color when recording
- **Recording Indicator**: Visual feedback showing recording status
- **Text Input Area**: Where transcribed text appears progressively
- **Status Display**: Shows current state (recording/standby)

### Styling

The system includes custom CSS for:

- Animated microphone button with pulse effect
- Recording status indicators
- Responsive design for mobile devices
- Dark mode compatibility

## 🔧 Configuration

### Language Settings

```python
# For Cantonese (Hong Kong)
language = "yue-HK"

# For Chinese (Hong Kong) - fallback
language = "zh-HK"
```

### Custom Styling

You can customize the appearance by modifying the CSS in the `enhanced_voice_input.py` file:

```css
.voice-input-container {
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    background-color: #f9f9f9;
}

.pulse {
    animation: pulse 1.5s infinite;
}
```

## 📱 Mobile Support

The voice input system is fully responsive and works on:

- Desktop computers
- Tablets
- Mobile phones
- Touch devices

## 🎯 Best Practices

### For Better Accuracy

1. **Speak Clearly**: Enunciate words properly
2. **Normal Pace**: Don't speak too fast or too slow
3. **Minimize Noise**: Use in quiet environments
4. **Good Microphone**: Use a quality microphone
5. **Standard Pronunciation**: Use standard Cantonese pronunciation

### Example Phrases

**Mathematics:**
- "五加三等於八" (Five plus three equals eight)
- "二分之一加三分之一" (One half plus one third)
- "請幫我計算這個分數" (Please help me calculate this fraction)

**General Conversation:**
- "你好，我想問一個問題" (Hello, I want to ask a question)
- "這個答案對不對？" (Is this answer correct?)
- "可以解釋一下嗎？" (Can you explain this?)

## 🛠️ Troubleshooting

### Common Issues

1. **No Audio Input**
   - Check microphone permissions
   - Ensure microphone is not muted
   - Try refreshing the page

2. **Poor Recognition**
   - Speak more clearly
   - Reduce background noise
   - Check internet connection (for Google Speech Recognition)

3. **Browser Compatibility**
   - Use modern browsers (Chrome, Firefox, Safari, Edge)
   - Enable JavaScript
   - Allow microphone access

### Error Messages

- **"Speech recognition not supported"**: Use a modern browser
- **"Microphone access denied"**: Allow microphone permissions
- **"No speech detected"**: Speak louder or check microphone

## 🔄 Integration with Existing Code

The enhanced voice input system is designed to be a drop-in replacement for the existing voice input:

```python
# Old way
from voice_input import record_voice
speech_input = record_voice("yue_hk")

# New way
from enhanced_voice_input import simple_voice_input
speech_input = simple_voice_input("語音輸入", key="chat_voice")
```

## 📊 Performance

- **Latency**: Real-time transcription with minimal delay
- **Accuracy**: High accuracy for Cantonese speech
- **Resource Usage**: Minimal CPU and memory usage
- **Network**: Works offline with Web Speech API

## 🔮 Future Enhancements

Potential improvements:

- Support for more languages
- Custom vocabulary training
- Noise cancellation
- Voice activity detection
- Confidence scoring display
- Multiple speaker support

## 📄 License

This enhanced voice input system is part of the Chat Math project and follows the same licensing terms.

## 🤝 Contributing

To contribute to the voice input system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions about the voice input system:

1. Check the troubleshooting section
2. Review the demo application (`voice_input_demo.py`)
3. Test with different browsers and devices
4. Report issues with detailed information

---

**🎤 Happy Voice Input!** 🎤 