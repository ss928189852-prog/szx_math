import streamlit as st
from voice_input_9_18 import record_voice
from voice_output_9_18 import generate_voice
import os
import crewAI_chatbot_qwen3_nothink
from translator_honor import translate_tw, translate_cn, translate_hk
import asyncio
import re
import html



# Set TOKENIZERS_PARALLELISM to false
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Chatbot:
    def __init__(self):
        # Initialize history and messages if they do not exist
        if "history" not in st.session_state and \
                "messages_cn" not in st.session_state and \
                "messages_tw" not in st.session_state and \
                "check_message_for_understanding" not in st.session_state:
            st.session_state["history"] = []  # initialize the conversation history
            st.session_state["messages_cn"] = []  # initialize the messages in simplified Chinese
            st.session_state["messages_tw"] = []  # initialize the messages in traditional Chinese
            st.session_state["check_messages"] = []  # initialize the messages for checking student understanding
            st.session_state["current_explanations"] = []
            st.session_state["current_scale"] = []
            st.session_state["current_choice"] = ""
            st.session_state["current_solution_stage"] = 0

    # a function to translate simplified Chinese to traditional Chinese
    def sync_translate_tw(self, text):
        return asyncio.run(translate_tw(text))

    # Process the first default student prompt
    def process_start_prompt(self):
        if st.session_state["is_first_user_prompt"]:  # if this is the first use prompt
            self.choice_made = False
            if st.session_state["current_num_solutions"] == 3:
                if st.session_state["current_solution_stage"] == 0:
                    option = st.radio('你選擇哪一個計算策略：A.由左至右順序計算；B.調換運算次序', ('', 'A', 'B'), index=0)
                    if st.button('确定', key="1"):
                        if option == "A":
                            st.session_state["current_solution_stage"] = 1
                            print("Selected A")
                            st.rerun()
                        elif option == "B":
                            st.session_state["current_explanations"] = st.session_state["current_explanation_C"]
                            st.session_state["current_scale"] = st.session_state["current_scale_C"]
                            st.session_state["current_choice"] = "C"
                            self.choice_made = True
                elif st.session_state["current_solution_stage"] == 1:
                    option_A = st.radio('你選擇：A. 先計首兩個分數；B. 同時計算三個分數', ('', 'A', 'B'))
                    if st.button('确定', key="2"):
                        if option_A == "A":
                            print("Selected AA")
                            st.session_state["current_explanations"] = st.session_state["current_explanation_A"]
                            st.session_state["current_scale"] = st.session_state["current_scale_A"]
                            st.session_state["current_choice"] = "A"
                            self.choice_made = True
                        elif option_A == "B":
                            print("Selected AB")
                            st.session_state["current_explanations"] = st.session_state["current_explanation_B"]
                            st.session_state["current_scale"] = st.session_state["current_scale_B"]
                            st.session_state["current_choice"] = "B"
                            self.choice_made = True
            elif st.session_state["current_num_solutions"] == 2:
                option = st.radio('你選擇：A. 先計首兩個分數；B. 同時計算三個分數', ('', 'A', 'B'))
                if st.button('确定', key="3"):
                    if option == "A":
                        st.session_state["current_explanations"] = st.session_state["current_explanation_A"]
                        st.session_state["current_scale"] = st.session_state["current_scale_A"]
                        st.session_state["current_choice"] = "A"
                        self.choice_made = True
                    elif option == "B":
                        st.session_state["current_explanations"] = st.session_state["current_explanation_B"]
                        st.session_state["current_scale"] = st.session_state["current_scale_B"]
                        st.session_state["current_choice"] = "B"
                        self.choice_made = True
            elif st.session_state["current_num_solutions"] == 1:
                st.session_state["current_explanations"] = st.session_state["current_explanation_A"]
                st.session_state["current_scale"] = st.session_state["current_scale_A"]
                st.session_state["current_choice"] = "A"
                self.choice_made = True
            if self.choice_made:
                explanation = st.session_state["current_explanations"][st.session_state["current_explanation_index"]]
                agent_text = explanation
                st.session_state["history"].append({"role": "assistant", "content": agent_text})
                agent_text_output = self.sync_translate_tw(agent_text)
                st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_output})
                st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})   # show only tutor's message
                st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                st.session_state["is_first_user_prompt"] = False         # update the prompt status
                st.rerun()
    def remove_html_tags(self, text):
        clean = re.compile('<.*?>')  # Matches any HTML tag
        return re.sub(clean, '', text)

    def convert_latex_to_html_fractions(self, text):
        """Convert LaTeX fractions to HTML/CSS fractions for proper display"""
        import re
        
        mixed_fraction_pattern = r'(\d+)\\frac\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(mixed_fraction_pattern, r'\1 \2/\3', text)

        # 2. 再处理独立分数：\frac{...}{...} → .../...
        # 同样，用 [^}]+ 匹配任意非闭合花括号的内容
        standalone_fraction_pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'
        text = re.sub(standalone_fraction_pattern, r'\1/\2', text)
        # 1. 先处理混合数：n\frac{...}{...} → n (...)/...
        # 原始只支持 \d+，现在允许分子分母是任意非 } 内容
        # mixed_fraction_pattern = r'(\d+)\\frac\{([^}]+)\}\{([^}]+)\}'
        # text = re.sub(mixed_fraction_pattern, r'\1 \2/\3', text)

        # 2. 再处理独立分数：\frac{...}{...} → .../...
        # 同样，用 [^}]+ 匹配任意非闭合花括号的内容
        # standalone_fraction_pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'
        # text = re.sub(standalone_fraction_pattern, r'\1/\2', text)
        # guard = r'(?<![=\'"])'
        # text = re.sub(guard + r'(\d+)\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1 \2/\3', text)
        # text = re.sub(guard + r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'\1/\2', text)
        # Convert mixed fractions: "1\frac{4}{5}" → "1 4/5"
        # mixed_fraction_pattern = r'(\d+)\\frac\{(\d+)\}\{(\d+)\}'
        # text = re.sub(mixed_fraction_pattern, r'\1 \2/\3', text)
        
        # # Convert standalone fractions: "\frac{3}{10}" → "3/10"
        # standalone_fraction_pattern = r'\\frac\{(\d+)\}\{(\d+)\}'
        # text = re.sub(standalone_fraction_pattern, r'\1/\2', text)
        
        # Remove LaTeX dollar signs
        text = text.replace('$', '')
        
        return text

    def format_multiple_choice_options(self, text):
        """Format multiple choice options to display each option on a separate line"""
        import re
        
        # Add double line breaks before each option (A), B), C), D)) to ensure proper separation in markdown
        # This regex matches option patterns like "A)", "B)", "C)", "D)" and adds double line breaks before them
        text = re.sub(r'([A-D]\)\s*)', r'\n\n\1', text)
        
        # Remove any leading line breaks if they exist
        text = text.lstrip('\n')
        
        return text


    # Converts LaTeX-style fractions (e.g., $\frac{1}{5} + \frac{1}{4}$) into standard fraction notation (e.g., 1/5 + 1/4) for correct pronunciation.
    def convert_expression_to_spoken_text(self, latex_str):
       # Remove all "$" signs
       converted_str = latex_str.replace("$", "")
       # Remove html tags
       converted_str = self.remove_html_tags(converted_str)
       # Convert mixed fractions: "5\frac{1}{3}" → "5又3分之1" for correct Cantonese pronunciation
       mixed_fraction_pattern = r"(\d+)\\frac\{(\d+)\}\{(\d+)\}"
       converted_str = re.sub(mixed_fraction_pattern, r"\1又\3份之\2", converted_str)
       # Convert standalone fractions: "\frac{1}{3}" → "3分之1"
       standalone_fraction_pattern = r"\\frac\{(\d+)\}\{(\d+)\}"
       converted_str = re.sub(standalone_fraction_pattern, r"\2份之\1", converted_str)
       # Replace "分" with "份" for correct Cantonese pronunciation
       converted_str = converted_str.replace("分數", "份數")
       converted_str = converted_str.replace("分母", "份母")
       converted_str = converted_str.replace("分子", "份子")
       converted_str = converted_str.replace("擴分", "擴份")
       converted_str = converted_str.replace("通分", "通份")
       # Replace operators with words for correct Cantonese pronunciation
       converted_str = converted_str.replace("+", "加")
       converted_str = converted_str.replace("-", "減")
       converted_str = converted_str.replace("x", "乘")
       return converted_str
    # Display chat messages
    def display_messages(self, in_sidebar=False):
        # st.subheader("輔導機械人🤖")
        self.process_start_prompt()
        if self.choice_made:

            for i, message in enumerate(st.session_state["messages_tw"]):
                role = message["role"]
                content = message["content"]

                # Set custom avatars for user and assistant
                if role == "user":
                    avatar = "🧒🏻"  # Custom avatar for user (e.g., Student emoji)
                elif role == "assistant":
                    avatar = "🤖"  # Custom avatar for assistant (e.g., Robot emoji)
                else:
                    avatar = None  # Default avatar for other roles

                # Use st.chat_message to display messages
                if role == "assistant":
                   # System message on the left
                   col1, col2 = st.columns([3, 1])
                   with col1:
                       # Convert LaTeX fractions to natural form and format multiple choice options
                       content_with_natural_fractions = self.convert_latex_to_html_fractions(content)
                       formatted_content = self.format_multiple_choice_options(content_with_natural_fractions)
                       formatted_content = html.escape(formatted_content).replace('\n', '<br>')
                    #    formatted_content = html.escape(formatted_content)
                       st.markdown(f"""
                       <style>
                       /* Make LaTeX fractions larger */
                       .katex {{
                           font-size: 1.5em !important;
                       }}
                       .katex-display {{
                           font-size: 1.5em !important;
                       }}
                       /* Target specific fraction elements */
                       .katex .frac-line {{
                           font-size: 1.5em !important;
                       }}
                       .katex .frac-num {{
                           font-size: 1.5em !important;
                       }}
                       .katex .frac-den {{
                           font-size: 1.5em !important;
                       }}
                       </style>
                       <div style="display: flex; align-items: start; margin-bottom: 10px;">
                           <div style="margin-right: 10px; font-size: 20px;">{avatar}</div>
                           <div style="background-color: #808080; color: white; padding: 10px; border-radius: 18px; width: fit-content; max-width: 80%; min-width: 100px; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                               {formatted_content}
                               <div style="position: absolute; left: -8px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-right: 8px solid #808080; border-top: 8px solid transparent; border-bottom: 8px solid transparent;"></div>
                           </div>
                       </div>
                       """, unsafe_allow_html=True)
                       
                       # Add minimal audio playback control for sidebar
                       if in_sidebar:
                           # Generate audio for this message
                           spoken_content = self.convert_expression_to_spoken_text(content)
                           audio_buffer = generate_voice(spoken_content)
                           st.markdown("""
                           <style>
                              audio {
                                width: 200px !important;
                                height: 30px !important;
                                background-color: #D3D3D3 !important;
                                border: 1px solid #D3D3D3 !important;
                                border-radius: 8px;
                                margin: -25px 0px 5px 33px !important;
                                display: block;
                              }     
                              /* Webkit browsers (Chrome, Safari) */
                              audio::-webkit-media-controls-panel {
                                background-color: #D3D3D3 !important;
                                border-radius: 8px;
                              }
                              audio::-webkit-media-controls-play-button {
                                background-color: white !important;
                                border-radius: 50%;
                              }
                              audio::-webkit-media-controls-volume-slider {
                                background-color: white !important;
                              }
                              /* Firefox */
                              audio::-moz-media-controls-panel {
                                background-color: #D3D3D3 !important;
                                border-radius: 8px;
                              }
                              /* Edge */
                              audio::-ms-media-controls-panel {
                                background-color: #D3D3D3 !important;
                                border-radius: 8px;
                              }
                              /* General audio styling for all browsers */
                              audio::-webkit-media-controls {
                                background-color: #D3D3D3 !important;
                              }
                              audio::-webkit-media-controls-enclosure {
                                background-color: #D3D3D3 !important;
                              }
                           </style>
                           """, unsafe_allow_html=True)
                           st.audio(audio_buffer, format="audio/mpeg", loop=False, autoplay=False)



                           # Display audio player closer to message
                        #    st.markdown("""
                        #    <style>
                        #       audio {
                        #         width: 40px !important;
                        #         height: 30px !important;
                        #         background-color: #D3D3D3 !important;
                        #         border: 1px solid #D3D3D3 !important;
                        #         border-radius: 8px;
                        #         margin: -25px 0px 5px 33px !important;
                        #         display: block;
                        #       }     
                        #       /* Webkit browsers (Chrome, Safari) */
                        #       audio::-webkit-media-controls-panel {
                        #         background-color: #D3D3D3 !important;
                        #         border-radius: 8px;
                        #       }
                        #       audio::-webkit-media-controls-play-button {
                        #         background-color: white !important;
                        #         border-radius: 50%;
                        #       }
                        #       audio::-webkit-media-controls-volume-slider {
                        #         background-color: white !important;
                        #       }
                        #       /* Firefox */
                        #       audio::-moz-media-controls-panel {
                        #         background-color: #D3D3D3 !important;
                        #         border-radius: 8px;
                        #       }
                        #       /* Edge */
                        #       audio::-ms-media-controls-panel {
                        #         background-color: #D3D3D3 !important;
                        #         border-radius: 8px;
                        #       }
                        #       /* General audio styling for all browsers */
                        #       audio::-webkit-media-controls {
                        #         background-color: #D3D3D3 !important;
                        #       }
                        #       audio::-webkit-media-controls-enclosure {
                        #         background-color: #D3D3D3 !important;
                        #       }
                        #    </style>
                        #    """, unsafe_allow_html=True)
                        #    st.audio(audio_buffer, format="audio/mpeg", loop=False, autoplay=False)
                           
                           # Show image after audio playback button if available
                        #    if st.session_state.get("sidebar_state") == "expanded":
                        #        try:
                        #            selected_quiz_file_name = st.session_state.get("selected_quiz_file_name", "LO_8_test")
                        #            num = st.session_state.get("current_guidance_step_index", 0) + 1
                        #            if st.session_state.get("current_num_guidance", 1) == 1:
                        #                image_path = f'./picture/{selected_quiz_file_name}/{st.session_state.get("current_question_index", 0)}_{num}.jpg'
                        #            else:
                        #                image_path = f'./picture/{selected_quiz_file_name}/{st.session_state.get("current_question_index", 0)}_{st.session_state.get("current_guidance_choice", 1)}_{num}.jpg'
                        #            if os.path.exists(image_path):
                        #                print(image_path)
                        #                image_a = Image.open(image_path)
                        #                st.image(image_a, use_container_width=True)
                        #        except Exception as e:
                        #            pass
                               
                        #        # Show data figure if available
                        #        if st.session_state.get("data_fig"):
                        #            st.pyplot(st.session_state["data_fig"])
                else:
                   # User message on the right
                   col1, col2 = st.columns([1, 3])
                   with col2:
                       st.markdown(f"""
                       <style>
                       /* Make LaTeX fractions larger */
                       .katex {{
                           font-size: 1.5em !important;
                       }}
                       .katex-display {{
                           font-size: 1.5em !important;
                       }}
                       /* Target specific fraction elements */
                       .katex .frac-line {{
                           font-size: 1.5em !important;
                       }}
                       .katex .frac-num {{
                           font-size: 1.5em !important;
                       }}
                       .katex .frac-den {{
                           font-size: 1.5em !important;
                       }}
                       </style>
                       <div style="display: flex; align-items: start; justify-content: flex-end; margin-bottom: 10px;">
                           <div style="background-color: #90EE90; color: black; padding: 10px; border-radius: 18px; width: fit-content; max-width: 80%; min-width: 100px; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                               {content}
                               <div style="position: absolute; right: -8px; top: 50%; transform: translateY(-50%); width: 0; height: 0; border-left: 8px solid #90EE90; border-top: 8px solid transparent; border-bottom: 8px solid transparent;"></div>
                           </div>
                           <div style="margin-left: 10px; font-size: 20px;">{avatar}</div>
                       </div>
                       """, unsafe_allow_html=True)
          
            st.session_state["thinking_spinner"] = st.empty()

           # Add CSS to align components on the same line"
            st.markdown("""
            <style>
            /* Force alignment of sidebar components */
            
            section[data-testid="stSidebar"] .stButton > div {
                margin-top: 0 !important;
                padding-top: 0 !important;
            }
            section[data-testid="stSidebar"] .stTextInput > div {
                margin-top: -29px !important;
                padding-top: 0 !important;
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stButton {
                margin-top: 9px !important;
                padding-top: 0 !important;
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
                margin-left: -15px !important;
            }
            
            /* Remove spacing between text input and button */
            section[data-testid="stSidebar"] .stTextInput {
                margin-right: 0 !important;
                padding-right: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stTextInput > div {
                margin-right: 0 !important;
                padding-right: 0 !important;
            }
            
            .stTextInput [title] {
                pointer-events: none !important;
            }
            
            /* Global audio styling - make all audio players light grey */
            audio {
                background-color: #D3D3D3 !important;
                border: 1px solid #D3D3D3 !important;
            }
            
            /* Webkit browsers (Chrome, Safari) */
            audio::-webkit-media-controls-panel {
                background-color: #D3D3D3 !important;
            }
            
            audio::-webkit-media-controls-play-button {
                background-color: white !important;
                border-radius: 50%;
            }
            
            audio::-webkit-media-controls-volume-slider {
                background-color: white !important;
            }
            
            /* Firefox */
            audio::-moz-media-controls-panel {
                background-color: #D3D3D3 !important;
            }
            
            /* Edge */
            audio::-ms-media-controls-panel {
                background-color: #D3D3D3 !important;
            }
            
            /* General audio styling for all browsers */
            audio::-webkit-media-controls {
                background-color: #D3D3D3 !important;
            }
            
            audio::-webkit-media-controls-enclosure {
                background-color: #D3D3D3 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            # Process the prompt if it is the start one
            # self.process_start_prompt()

            col1, col2, col3 = st.columns([4, 0.2, 1.8])  # Create two columns to display text input and speech input
            with st.container():
                with col1:
                    # Capture user input from text
                    if st.session_state["current_explanation_index"] <= len(
                            st.session_state["current_explanations"]) - 1:  # len(st.session_state["current_explanation"]):
                        print("Current step: " + str(st.session_state["current_explanation_index"]))
                        print("Current guidance length: " + str(len(st.session_state["current_explanations"])))
                        voice_text = st.session_state.get("voice_transcribed_text", "")

                        # Create text input that can be pre-populated with voice text
                        # Use empty string if voice_text is empty to clear the input
                        text_input = st.text_input(
                            label="輸入文字",
                            value="" if not voice_text else voice_text,
                            placeholder="輸入文字或使用語音輸入...",
                            label_visibility="hidden",
                            key=f"sidebar_input_{st.session_state.get('input_counter', 0)}"
                        )
                    else:
                        # end_message = "真棒！你已經完成了這道題的輔導！"
                        # st.session_state["show_messages"].append({"role": "assistant", "content": end_message})
                        # self.display_messages()
                        pass
                with col2:
                    # Capture user input from speech
                    if st.session_state["current_explanation_index"] <= len(
                            st.session_state["current_explanations"]) - 1:
                        # Submit button for the text input
                        if st.button("➤", key="send_button", use_container_width=True):
                            if text_input and text_input.strip():
                                st.session_state["text_input"] = text_input
                                # Clear voice text after processing
                                st.session_state["voice_transcribed_text"] = ""
                                # Increment counter to force new text input widget
                                st.session_state["input_counter"] = st.session_state.get("input_counter", 0) + 1
                                # Hide input elements immediately with CSS
                                st.markdown("""
                                <style>
                                section[data-testid="stSidebar"] .stTextInput,
                                section[data-testid="stSidebar"] .stButton {
                                    display: none !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                                self.process_input("text_input")
                    else:
                        # end_message = "真棒！你已經完成了這道題的輔導！"
                        # st.session_state["show_messages"].append({"role": "assistant", "content": end_message})
                        # self.display_messages()
                        pass
                # with col3:
                #    # Spacer column (empty)
                #    pass
                with col3:
                    # Voice input column
                    if st.session_state["current_explanation_index"] <= len(st.session_state["current_explanations"]) - 1:
                            speech_input = record_voice("yue_hk")
                    else:
                        pass



    # Process text input in chat window
    def process_input(self, input_key):
        user_input = st.session_state.get(input_key, "").strip()
        # if the user input is not empty
        if user_input:
            user_text = user_input
            question = st.session_state["current_question"]    # get the current question
            current_guidance_step_index = st.session_state["current_explanation_index"]  # get the current guidance step index
            # Retrieve the specific guidance step for problem-solving
            guidance_step = st.session_state["current_explanations"][current_guidance_step_index]
            # Retrieve the specific condition for passing a guidance step
            passing_condition = st.session_state["current_scale"][current_guidance_step_index]
            st.session_state["check_messages"].append({"role": "user", "content": user_text})
            check_messages = st.session_state["check_messages"]

            # Call the agent to check whether to move forward to the next guidance step based on student understanding
            print("In loop: current guidance step: " + str(current_guidance_step_index))
            with st.session_state["thinking_spinner"], st.spinner("處理中，請稍候 ..."):
               while crewAI_chatbot_qwen3_nothink.agent_check_move_to_next_explanation(question, guidance_step, passing_condition, check_messages):
                   # if reaching the end of all guidance steps
                   if st.session_state["current_explanation_index"] >= len(st.session_state["current_explanations"])-1:
                       end_message = "真棒！你已經完成了這道題的輔導！如果還未作答，記得完成答題哦！"
                       st.session_state["current_explanation_index"] += 1
                       st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                       st.session_state["messages_tw"].append({"role": "assistant", "content": end_message})
                       st.session_state["check_messages"] = []
                       st.rerun()
                       return
                   else:
                       st.session_state["current_explanation_index"] += 1  # move to the next guidance step
                       current_guidance_step_index = st.session_state["current_explanation_index"]  # get the current guidance step index
                       print("In loop: current guidance step: " + str(current_guidance_step_index))
                       guidance_step = st.session_state["current_explanations"][current_guidance_step_index]
                       passing_condition = st.session_state["current_scale"][current_guidance_step_index]

               print("Out of loop: current guidance step: " + str(current_guidance_step_index))
               # if the student has answered the tutor's question
               if crewAI_chatbot_qwen3_nothink.agent_check_is_explanation_answered(check_messages, guidance_step):
                   print("Starting error correction")
                   # call the agent tutor to further check whether student answer is incorrect
                   st.session_state["history"], agent_text = crewAI_chatbot_qwen3_nothink.agent_tutor(user_text, question, guidance_step, st.session_state["history"], passing_condition)
                   agent_text_display = self.sync_translate_tw(agent_text)
                   st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                   st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_display})
                   st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                   st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                   st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                   st.session_state[input_key] = ""    # Reset the input
                   st.rerun()  # Refresh the app's interface
               else:  # if the student has not answered the tutor's question
                   st.session_state["check_messages"] = []   # Reset the messages for checking understanding
                   agent_text = guidance_step
                   st.session_state["history"].append({"role": "user", "content": user_text})
                   st.session_state["history"].append({"role": "assistant", "content": agent_text})
                   agent_text_display = self.sync_translate_tw(agent_text)
                   st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                   st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_display})
                   st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                   st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                   st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                   st.session_state[input_key] = ""    # Reset the input
                   st.rerun()

