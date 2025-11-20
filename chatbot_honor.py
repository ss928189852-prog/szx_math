import streamlit as st
from voice_input import record_voice
from voice_output import generate_voice
import os
import crewAI_chatbot_honor
from translator_honor import translate_tw, translate_cn, translate_hk
import asyncio

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
                            print("选了A")
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
                            print("选了AA")
                            st.session_state["current_explanations"] = st.session_state["current_explanation_A"]
                            st.session_state["current_scale"] = st.session_state["current_scale_A"]
                            st.session_state["current_choice"] = "A"
                            self.choice_made = True
                        elif option_A == "B":
                            print("选了AB")
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

    # Display chat messages
    def display_messages(self):
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
                with st.chat_message(role, avatar=avatar):
                    st.markdown(content)
                    # if this is the last tutor message
                    if role == "assistant" and i >= len(st.session_state["messages_cn"]) - 2:
                        # generate and show the voice playback for the most recent tutor message only
                        audio_file = generate_voice(content)
                        # Inject custom CSS to style the audio player
                        st.markdown("""
                         <style>
                            audio {
                              width: 300px !important; /* Adjust the width of the audio player */
                              height: 20px; /* Set a specific height */
                              background-color: #f4f4f4; /* Change background color */
                              border-radius: 10px; /* Round corners */
                              margin: -20px 0px auto !important; /* Adjust margin top */
                              display: block;
                            }     
                            audio::-webkit-media-controls-panel {
                              background-color: #4CAF50; /* Green background */
                              border-radius: 10px;
                            }
                            audio::-webkit-media-controls-play-button {
                              background-color: white;
                              border-radius: 50%;
                            }
                            audio::-webkit-media-controls-volume-slider {
                              background-color: white;
                            }
                         </style>
                         """, unsafe_allow_html=True)
                        st.audio(audio_file, format="audio/mpeg", loop=False, autoplay=False)  # load the playback
                        os.remove(audio_file)  # delete the audio file

            st.session_state["thinking_spinner"] = st.empty()
            # Process the prompt if it is the start one
            # self.process_start_prompt()

            col1, col2 = st.columns([5, 1])  # Create two columns to display text input and speech input
            with col1:
                # Capture user input from text
                if st.session_state["current_explanation_index"] <= len(
                        st.session_state["current_explanations"]) - 1:  # len(st.session_state["current_explanation"]):
                    if text_input := st.chat_input("輸入文字"):
                        st.session_state["text_input"] = text_input
                        self.process_text()
                else:
                    # end_message = "真棒！你已經完成了這道題的輔導！"
                    # st.session_state["show_messages"].append({"role": "assistant", "content": end_message})
                    # self.display_messages()
                    pass

            with col2:
                # Capture user input from speech
                if st.session_state["current_explanation_index"] <= len(
                        st.session_state["current_explanations"]) - 1:  # len(st.session_state["current_explanation"]):
                    if speech_input := record_voice("yue_hk"):
                        st.session_state["speech_input"] = speech_input
                        self.process_speech()
                else:
                    # end_message = "真棒！你已經完成了這道題的輔導！"
                    # st.session_state["show_messages"].append({"role": "assistant", "content": end_message})
                    # self.display_messages()
                    pass



    # Process text input in chat window
    def process_text(self):
        # if the input text is not empty
        if (
                st.session_state["text_input"]
                and len(st.session_state["text_input"].strip()) > 0
        ):
            user_text = st.session_state["text_input"].strip()  # remove leading and trailing spaces
            question = st.session_state["current_question"]  # get the current question
            current_explanation_index = st.session_state[
                "current_explanation_index"]  # get the current explanation index
            # Retrieve the specific explanation step for problem-solving
            scale = st.session_state["current_scale"][current_explanation_index]
            explanation = st.session_state["current_explanations"][current_explanation_index]


            st.session_state["check_messages"].append({"role": "user", "content": user_text})
            check_messages = st.session_state["check_messages"]

            while crewAI_chatbot_honor.agent_check_move_to_next_explanation(question, explanation, scale, check_messages):
                st.session_state["current_explanation_index"] += 1
                if st.session_state["current_explanation_index"] > len(st.session_state["current_explanations"]) - 1:
                    end_message = "真棒！你已經完成了這道題的輔導！"
                    st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                    st.session_state["messages_tw"].append({"role": "assistant", "content": end_message})
                    st.rerun()
                    return
                else:
                    print("循环中：" + str(st.session_state["current_explanation_index"]))
                    explanation = st.session_state["current_explanations"][st.session_state["current_explanation_index"]]
                    scale = st.session_state["current_scale"][st.session_state["current_explanation_index"]]
            print("出循环：" + str(st.session_state["current_explanation_index"]))
            if crewAI_chatbot_honor.agent_check_is_explanation_answered(check_messages, explanation):
                print("有回答开始纠错")
                with st.session_state["thinking_spinner"], st.spinner("處理中 ..."):
                    st.session_state["history"], agent_text = crewAI_chatbot_honor.agent_tutor(user_text, question,
                                                                                             explanation,
                                                                                             st.session_state[
                                                                                                 "history"])
                agent_text_output = self.sync_translate_tw(agent_text)
                st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_output})
                st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                st.session_state["text_input"] = ""
                st.rerun()
            else:
                st.session_state["check_messages"] = []
                agent_text = explanation
                st.session_state["history"].append({"role": "user", "content": user_text})
                st.session_state["history"].append({"role": "assistant", "content": agent_text})
                agent_text_output = self.sync_translate_tw(agent_text)
                st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_output})
                st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                st.session_state["text_input"] = ""
                st.rerun()



    # Process speech input in chat window
    def process_speech(self):
        if (
                st.session_state["speech_input"]
                and len(st.session_state["speech_input"].strip()) > 0
        ):
            
            user_text = st.session_state["speech_input"].strip()  # remove leading and trailing spaces
            question = st.session_state["current_question"]  # get the current question
            current_explanation_index = st.session_state[
                "current_explanation_index"]  # get the current explanation index
            # Retrieve the specific explanation step for problem-solving
            explanation = st.session_state["current_explanations"][current_explanation_index]
            scale = st.session_state["current_scale"][current_explanation_index]
            st.session_state["check_messages"].append({"role": "user", "content": user_text})
            check_messages = st.session_state["check_messages"]
            while crewAI_chatbot_honor.agent_check_move_to_next_explanation(question, explanation, scale, check_messages):
                st.session_state["current_explanation_index"] += 1
                if st.session_state["current_explanation_index"] > len(st.session_state["current_explanations"]) - 1:
                    end_message = "真棒！你已經完成了這道題的輔導！"
                    st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                    st.session_state["messages_tw"].append({"role": "assistant", "content": end_message})
                    st.rerun()
                    return
                else:
                    print("循环中：" + str(st.session_state["current_explanation_index"]))
                    explanation = st.session_state["current_explanations"][st.session_state["current_explanation_index"]]
                    scale = st.session_state["current_scale"][st.session_state["current_explanation_index"]]
            print("出循环：" + str(st.session_state["current_explanation_index"]))
            if crewAI_chatbot_honor.agent_check_is_explanation_answered(check_messages, explanation):
                with st.session_state["thinking_spinner"], st.spinner("處理中 ..."):
                    st.session_state["history"], agent_text = crewAI_chatbot_honor.agent_tutor(user_text, question,
                                                                                             explanation,
                                                                                             st.session_state[
                                                                                                 "history"])
                agent_text_output = self.sync_translate_tw(agent_text)
                st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_output})
                st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                st.session_state["speech_input"] = ""
                st.rerun()
            else:
                st.session_state["check_messages"] = []
                agent_text = explanation
                st.session_state["history"].append({"role": "user", "content": user_text})
                st.session_state["history"].append({"role": "assistant", "content": agent_text})
                agent_text_output = self.sync_translate_tw(agent_text)
                st.session_state["messages_tw"].append({"role": "user", "content": user_text})
                st.session_state["messages_tw"].append({"role": "assistant", "content": agent_text_output})
                st.session_state["messages_cn"].append({"role": "user", "content": user_text})
                st.session_state["messages_cn"].append({"role": "assistant", "content": agent_text})
                st.session_state["check_messages"].append({"role": "assistant", "content": agent_text})
                st.session_state["speech_input"] = ""
                st.rerun()

