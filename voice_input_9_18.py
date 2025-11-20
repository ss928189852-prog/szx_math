import streamlit as st
from streamlit_mic_recorder import speech_to_text
import time

# def record_voice(language):
#     """
#     Fixed version: No more 'previous result' issue
#     - Uses session_state + st.rerun() like the original sr version
#     - Single button (mic)
#     - Auto-recognize on stop
#     """
#     # Language mapping
#     language_mapping = {
#         "yue_hk": "yue-HK",
#         "zh": "zh-TW",
#         "zh-cn": "zh-CN",
#         "en": "en-US"
#     }
#     google_language = language_mapping.get(language, "yue-HK")

#     # Initialize session state
#     if "is_recording" not in st.session_state:
#         st.session_state["is_recording"] = False
#     if "recorded_text" not in st.session_state:
#         st.session_state["recorded_text"] = ""
#     if "voice_transcribed_text" not in st.session_state:
#         st.session_state["voice_transcribed_text"] = ""

#     # Status placeholder
#     status_placeholder = st.empty()

#     # Show recording status
#     if st.session_state["is_recording"]:
#         status_placeholder.markdown("""
#         <div style="background-color: #e7f3ff; border: 1px solid #2196F3; border-radius: 4px; padding: 10px; margin: 10px 0 -10px -160px; text-align: left;">
#             🎤 請說話 (按 ⏹️ 停止)
#         </div>
#         """, unsafe_allow_html=True)

#     # Single mic button using streamlit_mic_recorder
#     text = speech_to_text(
#         start_prompt="🎤",
#         stop_prompt="⏹️",
#         language=google_language,
#         use_container_width=True,
#         just_once=True,
#         key="voice_recorder"
#     )

#     # Handle recognition result
#     if text is not None:
#         st.session_state["is_recording"] = False
#         recognized_text = text.strip()

#         # Clear status
#         status_placeholder.empty()

#         if recognized_text:
#             # ✅ 更新全局状态
#             st.session_state["recorded_text"] = recognized_text
#             st.session_state["voice_transcribed_text"] = recognized_text
#             st.session_state["input_counter"] = st.session_state.get("input_counter", 0) + 1

#             # ✅ 显示成功
#             status_placeholder.markdown(f"""
#             <div style="background-color: #e8f5e8; border: 1px solid #4caf50; border-radius: 4px; padding: 10px; margin: 10px 0 -10px -160px; text-align: left;">
#                 ✅ 語音識別完成: {recognized_text}
#             </div>
#             """, unsafe_allow_html=True)

#             time.sleep(1.5)
#             status_placeholder.empty()

#             # ✅ 关键：触发重运行，让外部读取最新值
#             st.rerun()

#         else:
#             status_placeholder.markdown("""
#             <div style="background-color: #ffebee; border: 1px solid #f44336; border-radius: 4px; padding: 10px; margin: 10px 0 -10px -160px; text-align: left;">
#                 ❌ 沒有識別到語音
#             </div>
#             """, unsafe_allow_html=True)
#             time.sleep(1.5)
#             status_placeholder.empty()

#     # Sync recording state from recorder
#     st.session_state["is_recording"] = bool(st.session_state.get("voice_recorder", False))

#     return None  # ❗不返回结果，靠 session_state 和 rerun 同步
def record_voice(language):
    # """
    # 语音输入组件（麦克风按钮）
    # - 使用 streamlit_mic_recorder 实现语音识别
    # - 提示信息显示在按钮下方，避免界面跳动
    # - 识别完成后自动更新 st.session_state 并刷新页面
    # - 外部应通过 st.session_state['voice_transcribed_text'] 获取识别结果

    # Args:
    #     language (str): 语言代码，支持 "yue_hk", "zh", "zh-cn", "en"
    # """
    # # 语言映射
    # language_mapping = {
    #     "yue_hk": "yue-HK",  # 粤语（香港）
    #     "zh": "zh-TW",       # 中文（繁体）
    #     "zh-cn": "zh-CN",    # 中文（简体）
    #     "en": "en-US"        # 英语
    # }
    # google_language = language_mapping.get(language, "yue-HK")

    # # 初始化 session_state
    # if "is_recording" not in st.session_state:
    #     st.session_state["is_recording"] = False
    # if "voice_transcribed_text" not in st.session_state:
    #     st.session_state["voice_transcribed_text"] = ""
    # if "input_counter" not in st.session_state:
    #     st.session_state["input_counter"] = 0

    # # ===== 第一步：渲染语音识别按钮 =====
    # text = speech_to_text(
    #     start_prompt="🎤 语音输入",
    #     stop_prompt="⏹️ 停止录音",
    #     language=google_language,
    #     use_container_width=True,
    #     just_once=True,  # 每次只识别一次
    #     key="voice_recorder"  # 必须有 key 才能记录状态
    # )

    # # 同步 recording 状态（用于 UI 反馈）
    # st.session_state["is_recording"] = bool(st.session_state.get("voice_recorder", False))

    # # ===== 第二步：在按钮下方显示状态提示（关键：避免按钮跳动）=====
    # status_placeholder = st.empty()  # 占位符放在按钮之后

    # if text is not None:
    #     # 停止录音
    #     st.session_state["is_recording"] = False
    #     recognized_text = text.strip()

    #     # 清除旧提示
    #     status_placeholder.empty()

    #     if recognized_text:
    #         # ✅ 成功识别
    #         st.session_state["voice_transcribed_text"] = recognized_text
    #         st.session_state["input_counter"] += 1

    #         status_placeholder.markdown(f"""
    #         <div style="
    #             background-color: #e8f5e8;
    #             border: 1px solid #4caf50;
    #             border-radius: 4px;
    #             padding: 10px;
    #             margin: 10px 0;  /* 上下留白一致 */
    #             font-size: 14px;
    #         ">
    #             ✅ 語音識別完成: <strong>{recognized_text}</strong>
    #         </div>
    #         """, unsafe_allow_html=True)

    #         # 等待用户看到结果
    #         time.sleep(1.2)
    #         status_placeholder.empty()  # 清除提示

    #         # 🔁 关键：触发重运行，让外部立即读取新值
    #         st.rerun()

    #     else:
    #         # ❌ 未识别到语音
    #         status_placeholder.markdown("""
    #         <div style="
    #             background-color: #ffebee;
    #             border: 1px solid #f44336;
    #             border-radius: 4px;
    #             padding: 10px;
    #             margin: 10px 0;
    #             font-size: 14px;
    #         ">
    #             ❌ 沒有識別到語音，請重試
    #         </div>
    #         """, unsafe_allow_html=True)

    #         time.sleep(1.5)
    #         status_placeholder.empty()

    # # 返回 None（外部不依赖返回值）
    # return None
    language_mapping = {
        "yue_hk": "yue-HK",  # 粤语（香港）
        "zh": "zh-TW",       # 中文（繁体）
        "zh-cn": "zh-CN",    # 中文（简体）
        "en": "en-US"        # 英语
    }
    google_language = language_mapping.get(language, "yue-HK")

    # 初始化 session_state
    if "is_recording" not in st.session_state:
        st.session_state["is_recording"] = False
    if "voice_transcribed_text" not in st.session_state:
        st.session_state["voice_transcribed_text"] = ""
    if "input_counter" not in st.session_state:
        st.session_state["input_counter"] = 0

    # ===== 第一步：使用 speech_to_text 渲染按钮 =====
    text = speech_to_text(
        start_prompt="🎤 語音輸入",
        stop_prompt="⏹️ 停止錄音",
        language=google_language,
        use_container_width=True,
        just_once=True,
        key="voice_recorder"
    )

    # 同步 recording 状态（用于 UI 反馈）
    st.session_state["is_recording"] = bool(st.session_state.get("voice_recorder", False))



    # ===== 第四步：状态提示（在按钮下方）=====
    status_placeholder = st.empty()

    if text is not None:
        st.session_state["is_recording"] = False
        recognized_text = text.strip()

        status_placeholder.empty()  # 清除旧提示

        if recognized_text:
            # ✅ 成功识别
            st.session_state["voice_transcribed_text"] = recognized_text
            st.session_state["input_counter"] += 1

            status_placeholder.markdown(f"""
            <div style="
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;  /* 上下留白一致 */
                font-size: 14px;
            ">
                ✅ 語音識別完成: <strong>{recognized_text}</strong>
            </div>
            """, unsafe_allow_html=True)

            # 等待用户看到结果
            time.sleep(1.2)
            status_placeholder.empty()  # 清除提示

            # 🔁 关键：触发重运行，让外部立即读取新值
            st.rerun()

        else:
            # ❌ 未识别到语音
            status_placeholder.markdown("""
            <div style="
                background-color: #ffebee;
                border: 1px solid #f44336;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
                font-size: 14px;
            ">
                ❌ 沒有識別到語音，請重試
            </div>
            """, unsafe_allow_html=True)

            time.sleep(1.5)
            status_placeholder.empty()

    return None