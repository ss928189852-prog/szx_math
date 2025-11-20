import streamlit as st
import json
import mysql
import matplotlib.pyplot as plt
import math
import re
import numpy as np
from math import pi
from streamlit_extras.add_vertical_space import add_vertical_space
import data_bar_chart_3
import crewAI_chatbot_qwen3_nothink
from translator_honor import translate_tw, translate_cn, translate_hk
import asyncio
import datetime
import time

class Quiz:
    quiz_data = None

    # Initialize session variables
    def __init__(self, questionbank):
        self.default_values = {'current_question_bank' : "",
                               'current_question_index': 0,  # the current question index
                               'current_question': [],  # the current question
                               'current_explanation_index': 0,  # the current explanation index

                               'denominators': [],  # the list of denominators in the question
                               'remaining_attempts': -1,  # the remaining number of attempts for the current question
                               'user_score': 0,  # the score achieved by the user
                               'selected_option': None,  # the answer selected by the user
                               'is_answer_submitted': False,  # the status of whether an answer is submitted
                               'is_answer_correct': False,  # the status of whether the submitted answer is correct
                               'prompt': [],  # the prompt content
                               'is_first_user_prompt': True,  # the status of whether this is the first user prompt
                               'messages_cn': [],  # the messages in simplifed Chinese
                               'messages_tw': [],  # the messages in traditional Chinese
                               'show_performance_analysis': False,  # the status of showing user performance analysis
                               'competence_domains': {},  # the competence domains demonstrated by the user
                               'error_domains': {},  # the error domains demonstrated by the user
                               'current_explanation_A': [],
                               'current_explanation_B': [],
                               'current_explanation_C': [],
                               'current_scale_A': [],
                               'current_scale_B': [],
                               'current_scale_C': [],
                               'lcm': [],
                               'current_num_solutions': 0,
                               'data_fig': None,
                               'start': False
                               }
        for key, value in self.default_values.items():
            st.session_state.setdefault(key, value)
        self.question_file_name = questionbank + ".json"
        st.session_state["current_question_bank"] = questionbank

    # Load quiz data
    def load_quiz(self):
        with open(r'.json/{}'.format(self.question_file_name), 'r', encoding='utf-8-sig') as f:
            self.quiz_data = json.load(f)

    def sync_translate_tw(self, text):
        return asyncio.run(translate_tw(text))



    # Perform actions when the 'help' button is clicked
    def help_clicked(self):
        # Change sidebar and button states
        st.session_state["sidebar_state"] = (
            "collapsed" if st.session_state["sidebar_state"] == "expanded" else "expanded"
        )
        st.session_state["button_label"] = (
            "關閉幫手🤖" if st.session_state["button_label"] == "開啟幫手🤖" else "開啟幫手🤖"
        )
        if st.session_state["button_label"] == "關閉幫手🤖":
            mysql.insert_chatbot_use_info(st.session_state["logged_user_name"] ,st.session_state["current_question_bank"], st.session_state["current_question_index"]+1)
        question_item = self.quiz_data[st.session_state["current_question_index"]]  # get the current question ID
        st.session_state["current_question"] = question_item['question']  # get the question
        st.session_state["current_num_solutions"] = question_item['num_solutions']
        st.session_state["current_solution_stage"] = 0
        st.session_state["current_choice"] = []
        if st.session_state["current_num_solutions"] == 3:
            st.session_state["current_explanation_A"] = question_item['explanation_A']
            st.session_state["current_scale_A"] = question_item['scale_A']
            st.session_state["current_explanation_B"] = question_item['explanation_B']
            st.session_state["current_scale_B"] = question_item['scale_B']
            st.session_state["current_explanation_C"] = question_item['explanation_C']
            st.session_state["current_scale_C"] = question_item['scale_C']
        elif st.session_state["current_num_solutions"] == 2:
            st.session_state["current_explanation_A"] = question_item['explanation_A']
            st.session_state["current_scale_A"] = question_item['scale_A']
            st.session_state["current_explanation_B"] = question_item['explanation_B']
            st.session_state["current_scale_B"] = question_item['scale_B']
        elif st.session_state["current_num_solutions"] == 1:
            st.session_state["current_explanation_A"] = question_item['explanation']
            st.session_state["current_scale_A"] = question_item['scale']
        # st.session_state["current_explanation"] = question_item['explanation']  # get the explanation of how to solve the question
        # st.session_state["current_scale"] = question_item['scale']
        if question_item['lcm']:
            st.session_state["lcm"] = question_item['lcm']
            st.session_state["data_fig"] = data_bar_chart_3.data_fig_original(st.session_state["lcm"])
        else:
            st.session_state["lcm"] = []
            st.session_state["data_fig"] = None


    # Perform actions to restart quiz
    def restart_quiz(self):
        # reset session variables - 使用赋值方式，自动创建不存在的键
        st.session_state["current_question_index"] = 0
        st.session_state["current_question"] = []
        st.session_state["current_explanation_index"] = 0
        st.session_state["current_explanations"] = []
        st.session_state["denominators"] = []
        st.session_state["remaining_attempts"] = -1
        st.session_state["user_score"] = 0
        st.session_state["selected_option"] = None
        st.session_state["is_answer_submitted"] = False
        st.session_state["is_answer_correct"] = False
        st.session_state["prompt"] = []
        st.session_state["is_first_user_prompt"] = True
        st.session_state["messages_cn"] = []
        st.session_state["messages_tw"] = []
        st.session_state["show_performance_analysis"] = False
        st.session_state["competence_domains"] = {}
        st.session_state["error_domains"] = {}
        st.session_state["check_messages"] = []
        st.session_state["start"] = False
        # reset sidebar and button states
        st.session_state["sidebar_state"] = "collapsed"
        st.session_state["button_label"] = "開啟幫手🤖"
        
        # 重置进度条相关的状态 - 使用赋值方式重置，更安全
        st.session_state["data_fig"] = None
        st.session_state["lcm"] = None

        # Display the performance charts

    def get_student_performance_summary(self):
        summary = "能力得分（满分5分）：\n"
        # 先统计所有能力维度（不管得分是否为0）
        competence_full_scores = {}
        for i in range(st.session_state.get("current_question_index", 0) + 1):
            question_item = self.quiz_data[i]
            objective = question_item['objective']
            criteria = question_item['criteria']
            if objective not in competence_full_scores:
                competence_full_scores[objective] = {}
            if criteria not in competence_full_scores[objective]:
                competence_full_scores[objective][criteria] = 1
            else:
                competence_full_scores[objective][criteria] += 1
        # 汇总所有能力（包括0分），并进行标准化处理
        competence_domains = st.session_state.get("competence_domains", {})
        error_domains = st.session_state.get("error_domains", {})
        for obj in competence_full_scores:
            for cri in competence_full_scores[obj]:
                raw_score = competence_domains.get(obj, {}).get(cri, 0.0)
                full_score = competence_full_scores[obj][criteria]
                # 像雷达图绘制时一样进行标准化处理
                normalized_score = (raw_score / full_score) * 5 if full_score > 0 else 0
                summary += f"- {obj}（{cri}）：{normalized_score:.1f}分\n"
        summary += "\n错误类型统计：\n"
        for obj, err_dict in error_domains.items():
            summary += f"- {obj}：\n"
            for err, count in err_dict.items():
                summary += f"    - {err}：{count}次\n"
        prompt = (
            "你是一位小学数学老师。"
            "首先你要总结这位学生的表现，并进行一些分析，然后指出需要加强的地方，并给出1-2条学习建议。"
            "语言要简洁明了。只输出对学生说的话，不要输出其他内容。"
            "以下是这位学生的表现数据：\n" + summary
        )
        print(summary)
        advice = crewAI_chatbot_qwen3_nothink.get_llm_feedback(text=prompt)
        # 返回纯文本，去除可能的HTML标签，并将换行符转换为HTML段落
        import re
        # 移除HTML标签，保留纯文本
        clean_advice = re.sub(r'<[^>]+>', '', advice)
        # 将换行符转换为HTML段落标签，确保每个段落字体大小一致
        # 先处理双换行符（段落分隔）
        paragraphs = clean_advice.split('\n\n')
        formatted_paragraphs = []
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # 跳过空段落
                # 第一段不需要上边距，后续段落需要
                if i == 0:
                    formatted_paragraphs.append(f'<div style="font-size:1.1rem;">{paragraph.strip()}</div>')
                else:
                    formatted_paragraphs.append(f'<div style="font-size:1.1rem; margin-top:8px;">{paragraph.strip()}</div>')
        
        # 将段落内的单换行符转换为<br>
        formatted_advice = ''.join(formatted_paragraphs).replace('\n', '<br>')
        formatted_advice = self.sync_translate_tw(formatted_advice)
        return formatted_advice

    def get_ai_feedback_from_normalized_data(self):
        """直接使用标准化后的能力得分数据生成AI反馈"""
        summary_1 = "能力得分（满分5分）：\n"
        
        # 直接使用已经标准化后的competence_domains数据
        competence_domains = st.session_state.get("competence_domains", {})
        error_domains = st.session_state.get("error_domains", {})
        
        # 遍历标准化后的能力得分
        for obj, criteria_dict in competence_domains.items():
            for cri, score in criteria_dict.items():
                summary_1 += f"- {cri}：{score:.1f}分\n"
        
        summary = summary_1 + "\n错误类型统计：\n"
        for obj, err_dict in error_domains.items():
            summary += f"- {obj}：\n"
            for err, count in err_dict.items():
                summary += f"    - {err}：{count}次\n"
        
        prompt = (
            "你是一位小学数学老师。"
            "首先你要总结这位学生的表现，并进行一些分析，然后指出需要加强的地方，并给出1-2条学习建议。"
            "语言要简洁明了。只输出对学生说的话，不要输出其他内容。"
            "请使用繁体中文回答。"
            "以下是这位学生的表现数据：\n" + summary
        )
        advice = crewAI_chatbot_qwen3_nothink.get_llm_feedback(text=prompt)
        # 返回纯文本，去除可能的HTML标签，并将换行符转换为HTML段落
        import re
        # 移除HTML标签，保留纯文本
        clean_advice = re.sub(r'<[^>]+>', '', advice)
        # 将换行符转换为HTML段落标签，确保每个段落字体大小一致
        # 先处理双换行符（段落分隔）
        paragraphs = clean_advice.split('\n\n')
        formatted_paragraphs = []
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # 跳过空段落
                # 第一段不需要上边距，后续段落需要
                if i == 0:
                    formatted_paragraphs.append(f'<div style="font-size:1.1rem;">{paragraph.strip()}</div>')
                else:
                    formatted_paragraphs.append(f'<div style="font-size:1.1rem; margin-top:8px;">{paragraph.strip()}</div>')
        
        # 将段落内的单换行符转换为<br>
        formatted_advice = ''.join(formatted_paragraphs).replace('\n', '<br>')
        
        # 先提取纯文本进行翻译，然后重新格式化
        import re
        # 提取所有文本内容（去除HTML标签）
        text_content = re.sub(r'<[^>]+>', '', formatted_advice)
        
        # 翻译纯文本
        try:
            translated_text = self.sync_translate_tw(text_content)
        except Exception as e:
            print(f"Translation error: {e}")
            translated_text = text_content  # 如果翻译失败，使用原文
        
        # 重新应用HTML格式
        # 将翻译后的文本按段落分割并重新格式化
        paragraphs = translated_text.split('\n\n')
        formatted_translated_paragraphs = []
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # 跳过空段落
                # 第一段不需要上边距，后续段落需要
                if i == 0:
                    formatted_translated_paragraphs.append(f'<div style="font-size:1.1rem;">{paragraph.strip()}</div>')
                else:
                    formatted_translated_paragraphs.append(f'<div style="font-size:1.1rem; margin-top:8px;">{paragraph.strip()}</div>')
        
        # 将段落内的单换行符转换为<br>
        final_formatted_advice = ''.join(formatted_translated_paragraphs).replace('\n', '<br>')
        
        mysql.insert_ai_suggestion_info(st.session_state["logged_user_name"], summary_1, final_formatted_advice)
        return final_formatted_advice

    def start_performance_analysis_transition(self):
        """Start the performance analysis transition"""
        st.session_state["performance_analysis_transition"] = True

    def display_performance_analysis(self):
        st.session_state["sidebar_state"] = "collapsed"
        st.session_state["data_fig"] = None
        competence_full_scores = {}  # Dictionary to store full scores for each competence

        # Skip the first-time wait if already displayed via transition
        if st.session_state.get("show_performance_analysis_ready", False):
            st.session_state["show_performance_analysis_ready"] = False  # Reset the flag
            # Skip the first-time wait block and go directly to display
            pass
        elif not st.session_state.get("show_performance_analysis", False):
            st.session_state["show_performance_analysis"] = True
            
            # 显示加载动画
            with st.spinner("正在生成分析中..."):
                # 模拟加载时间
                import time
                time.sleep(2)
            return  # Exit early on first display
        
        # Display the performance analysis content
        if st.session_state.get("show_performance_analysis", False):
            # 新增：AI总结建议
            st.markdown(f'#### <div style="text-align: center; margin: 0; padding: 0; margin-top: -50px;">你的表現分析📊</div>',
                         unsafe_allow_html=True)

            # Prepare the dataset for generating charts
            for i in range(st.session_state["current_question_index"] + 1):
                question_item = self.quiz_data[i]
                objective = question_item['objective']
                criteria = question_item['criteria']

                # Calculate the full competence scores for each question item
                if objective not in competence_full_scores:
                    competence_full_scores[objective] = {}
                if criteria not in competence_full_scores[objective]:
                    competence_full_scores[objective][criteria] = 1
                else:
                    competence_full_scores[objective][criteria] += 1

                # Initialize user's competence domains if not present
                if objective not in st.session_state["competence_domains"]:
                    st.session_state["competence_domains"][objective] = {}
                if criteria not in st.session_state["competence_domains"][objective]:
                    st.session_state["competence_domains"][objective][criteria] = 0

            # Calculate competence scores
            for objective in st.session_state["competence_domains"]:
                for criteria in st.session_state["competence_domains"][objective]:
                    user_score = st.session_state["competence_domains"][objective][criteria]
                    full_score = competence_full_scores[objective][criteria]
                    # Compute the ratio and scale to a score between 0 and 5
                    score = (user_score / full_score) * 5
                    # score = user_score
                    print(f"score: {score}")
                    st.session_state["competence_domains"][objective][criteria] = score

            # 在能力得分标准化后，获取AI反馈
            st.markdown("<div style='background:#f6faff;border-radius:8px;padding:16px 18px 10px 18px;margin-bottom:10px;font-size:1.1rem;'><div style='font-size:1.1rem; font-weight:bold;'>老師的話：</div>" + self.get_ai_feedback_from_normalized_data() + "</div>", unsafe_allow_html=True)

            # Plot radar and donut charts for each competence domain
            # Set font properties for displaying Chinese characters
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False    # Ensure negative signs are displayed correctly

            for objective in st.session_state["competence_domains"]:
                categories = list(st.session_state["competence_domains"][objective].keys())
                scores = list(st.session_state["competence_domains"][objective].values())

                # 添加间距
                add_vertical_space(2)

                # 创建极坐标图
                fig1, ax1 = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})
                N = len(categories)

                if N == 1:
                    # 一维：画一条射线
                    angles = [0]
                    ax1.plot([0, 0], [0, scores[0]], linewidth=2, linestyle='-', color='blue', marker='o', markersize=6)
                    ax1.set_ylim(0, 5)
                    ax1.yaxis.grid(True, color='gray', linestyle='--', alpha=0.5)
                    ax1.set_xticks([0])
                    ax1.set_xticklabels([categories[0]], fontweight='bold', fontsize=9, fontname='Microsoft YaHei')
                    ax1.set_yticks([1, 2, 3, 4, 5])
                    ax1.set_yticklabels([1, 2, 3, 4, 5])
                    ax1.tick_params(axis='x', pad=20)
                    ax1.spines['polar'].set_visible(False)
                    ax1.set_title(f"{objective}:\n能力值", x=0.2, fontsize=11, fontweight='bold', pad=30, fontname='Microsoft YaHei')

                else:
                    # 多维情况
                    angles = [n / float(N) * 2 * pi for n in range(N)]
                    scores_extended = scores + scores[:1]
                    angles += angles[:1]

                    ax1.set_ylim(0, 5)
                    ax1.set_theta_offset(pi / 2)
                    ax1.set_theta_direction(-1)

                    ax1.plot(angles, scores_extended, linewidth=1, linestyle='solid', color='blue', marker='o', markersize=4)
                    ax1.fill(angles, scores_extended, alpha=0.4, color='blue')

                    ax1.yaxis.grid(color='gray', linestyle='--', alpha=0.4)
                    ax1.set_xticks(angles[:-1])
                    ax1.set_xticklabels(categories, fontweight='bold', fontsize=9, fontname='Microsoft YaHei')
                    ax1.set_yticks([1, 2, 3, 4, 5])
                    ax1.set_yticklabels([1, 2, 3, 4, 5])
                    ax1.tick_params(axis='x', pad=20)
                    ax1.spines['polar'].set_visible(False)
                    ax1.set_title(f"{objective}:\n能力值", x=0.0, fontweight='bold', fontsize=11, pad=40, fontname='Microsoft YaHei')
                st.pyplot(fig1)

                # Add vertical space
                add_vertical_space(2)  # Adds space equivalent to 2 lines
                # Plot Donut Chart
                if objective in st.session_state.get("error_domains", {}):
                    error_categories = list(st.session_state["error_domains"][objective].keys())
                    error_counts = list(st.session_state["error_domains"][objective].values())
                    fig2, ax2 = plt.subplots(figsize=(4, 4))
                    ax2.pie(
                        error_counts,
                        labels=error_categories,
                        autopct='%1.1f%%',
                        startangle=90,
                        wedgeprops=dict(width=0.7),
                        textprops={'fontsize': 9, 'fontname': 'Microsoft YaHei'}
                    )
                    # ax2.set_aspect('equal')
                    ax2.set_title(f"{objective}:\n錯誤概念分佈百分比", x=0.0, fontweight='bold', fontsize=11, pad=40,
                                  fontname='Microsoft YaHei')
                    st.pyplot(fig2)

            # Show the "restart" button at the end, centre-aligned and moved lower
            st.markdown(
                """
                <style>
                  div.stButton {
                    display: flex;
                    justify-content: center;
                    margin-top: 30px !important;
                  }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.button('重新開始🔄', on_click=self.restart_quiz)

    # Submit and check answer, and update score
    def submit_and_check_answer(self):
        question_item = self.quiz_data[st.session_state["current_question_index"]]
        st.session_state["is_answer_submitted"] = True  # update the session variable
        # Check if an option has been selected
        st.session_state["start"] = True
        if st.session_state["selected_option"] is not None and st.session_state["selected_option"] != "請選擇一個答案：":
            index = ord(question_item['answer']) - ord('A')
            # 检查是否有options_fig字段，如果没有则跳过生成图
            if question_item['options_fig']:
                option_data = question_item['options_fig'][index]
            else:
                option_data = None
            txt = ""
            # Decrement the remaining no. of attempts by 1
            st.session_state["remaining_attempts"] -= 1
            # if the selected option is correct
            if st.session_state["button_label"] == "關閉幫手🤖":
                chatbot_state = 1
            else:
                chatbot_state = 0
            mysql.insert_student_choice_info(st.session_state["logged_user_name"] ,st.session_state["current_question_bank"], st.session_state["current_question_index"]+1,
                                             st.session_state.selected_option[0], question_item['answer'], chatbot_state)
            self.end_datetime = datetime.datetime.now()
            self.end_time = time.time()
            duration = self.end_time - self.start_time
            duration = round(duration, 2)
            mysql.insert_exam_records_info(st.session_state["logged_user_name"] ,st.session_state["current_question_bank"], st.session_state["current_question_index"]+1,
                                             st.session_state.selected_option[0], question_item['answer'], self.start_datetime, self.end_datetime, duration)
            if st.session_state.selected_option[0] == question_item['answer']:
                txt = "你的答案（正確）"
                st.session_state["is_answer_correct"] = True
                st.session_state["user_score"] += 1  # increment the user score by 1
                # update the score for user competence
                objective = question_item['objective']
                criteria = question_item['criteria']
                # the number of answer options for the question (excluding the default option "請選擇一個答案：")
                option_count = len(question_item['options']) - 1
                # the competence score is dependent on the number of attempts made by the user for the same question
                competence_score = float(1 * ((st.session_state["remaining_attempts"] + 1) / (option_count - 1)))
                # add a new competence and assign a score
                if objective not in list(st.session_state["competence_domains"].keys()):
                    st.session_state["competence_domains"][objective] = {}
                if criteria not in list(st.session_state["competence_domains"][objective].keys()):
                    st.session_state["competence_domains"][objective][criteria] = competence_score
                # update the score for an existing competence
                else:
                    st.session_state["competence_domains"][objective][criteria] += competence_score
            else:  # if the selected option is correct
                txt = "你的答案（錯誤）"
                # update the count of user error
                print(type(st.session_state.selected_option))
                print(st.session_state.selected_option[0])
                objective = question_item['objective']
                error_index = ord(st.session_state.selected_option[0]) - ord('A')  # convert a letter into an index
                error_name = question_item['errors'][error_index]
                # add a new error and assign a count if not found. Otherwise, update the count
                if objective not in list(st.session_state["error_domains"].keys()):
                    st.session_state["error_domains"][objective] = {}
                if error_name not in list(st.session_state["error_domains"][objective].keys()):
                    st.session_state["error_domains"][objective][error_name] = 1
                else:
                    st.session_state["error_domains"][objective][error_name] += 1
            if st.session_state['remaining_attempts'] <= 0:
                st.session_state["lcm"] = question_item['lcm']
                st.session_state["data_fig"] = None
                # 如果没有lcm数据，重新加载当前题目的数据
                if option_data is not None and st.session_state["lcm"]:
                    st.session_state["data_fig"] = data_bar_chart_3.data_fig_final(st.session_state["lcm"], option_data)
                else:
                    st.session_state["data_fig"] = None

    # Reload the current question
    def reload_current_question(self):
        # reset some session variables
        st.session_state["selected_option"] = None
        st.session_state["is_answer_submitted"] = False

    # Go to the next question
    def next_question(self):
        st.session_state["current_question_index"] += 1  # update the current index
        # reset some session variables
        st.session_state["current_question"] = []
        st.session_state["current_explanation_index"] = 0
        st.session_state["current_explanations"] = []
        st.session_state["denominators"] = []
        st.session_state["remaining_attempts"] = -1
        st.session_state["selected_option"] = None
        st.session_state["is_answer_submitted"] = False
        st.session_state["is_answer_correct"] = False
        st.session_state["prompt"] = []
        st.session_state["is_first_user_prompt"] = True
        st.session_state["messages_cn"] = []
        st.session_state["messages_tw"] = []
        st.session_state["show_performance_analysis"] = False
        # reset sidebar and button states
        st.session_state["sidebar_state"] = "collapsed"
        st.session_state["button_label"] = "開啟幫手🤖"
        # 清空图表数据
        st.session_state["data_fig"] = None
        st.session_state["check_messages"] = []
        st.session_state["lcm"] = None

        # Display quiz progress and user score

    def display_progress_and_score(self):
        # Show the car progress bar
        if (st.session_state.get("is_answer_submitted", False) and 
            st.session_state.get("selected_option") and 
            st.session_state.get("selected_option") != "請選擇一個答案："):
            progress_bar_value = (st.session_state["current_question_index"] + 1) / len(self.quiz_data)
        else:
            progress_bar_value = st.session_state["current_question_index"] / len(self.quiz_data)
        st.markdown(
           f"""
           <style>
              [data-testid="stMetricValue"] {{
                  font-size: 30px;
              }}
              .car-progress-container {{
                   position: relative;
                   width: 100%;
                   height: 60px;
                   background: white;
                   margin: 10px 0;
                   margin-top: 10px; /* 原为-50px，改为10px，避免遮挡 */
                   overflow: hidden;
               }}
               @media (prefers-color-scheme: dark) {{
                   .car-progress-container {{
                       background: #ffffff !important;
                   }}
               }}
              .road {{
                   position: absolute;
                   bottom: 2px;
                   width: 100%;
                   height: 10px;
                   background: #696969;
                   border-top: 2px solid #FFD700;
               }}
              .car {{
                   position: absolute;
                   bottom: 20px;
                   left: calc({progress_bar_value * 100}% - 10px - ({progress_bar_value} * 40px));
                   width: 60px;
                   height: 25px;
                   transition: left 0.5s ease-in-out;
                   z-index: 10;
               }}
               .car::after {{
                   content: '🚗';
                   position: absolute;
                   top: -5px;
                   left: 15px;
                   font-size: 30px;
                   transform: scaleX(-1);
               }}
              .progress-text {{
                   position: absolute;
                   top: 0px;
                   left: 5px;
                   color: red;
                   font-weight: bold;
                   font-size: 16px;
               }}
               .progress-percentage {{
                   position: absolute;
                   top: 0px;
                   right: 10px;
                   color: red;
                   font-weight: bold;
                   font-size: 14px;
               }}
           </style>
           <div class="car-progress-container">
               <div class="progress-text">進度 ({int(progress_bar_value * 100)}%)</div>
               <div class="road"></div>
               <div class="car"></div>
           </div>
           """,
           unsafe_allow_html=True,
        )
        score_percentage = st.session_state["user_score"] / len(self.quiz_data)
        st.markdown(
           f"""
           <style>
              [data-testid="stMetricValue"] {{
                  margin-top: 5px;
              }}
              .score-bar-container {{
                   width: 100%;
                   height: 20px;
                   background-color: #f0f0f0;
                   border-radius: 12px;
                   overflow: hidden;
                   border: 1px solid green;
                   margin: -5px 0;
               }}
               @media (prefers-color-scheme: dark) {{
                   .score-bar-container {{
                       background-color: #ffffff !important;
                       border: 1px solid #ffffff !important;
                   }}
               }}
              .score-bar-fill {{
                  height: 100%;
                  background: linear-gradient(90deg, #4CAF50, #45a049);
                  width: {score_percentage * 100}%;
                  transition: width 0.5s ease-in-out;
                  border-radius: 10px;
              }}
              .score-text {{
                   position: absolute;
                   top: 50%;
                   left: 50%;
                   transform: translate(-50%, -50%);
                   color: black;
                   font-weight: bold;
                   font-size: 12px;
                   z-index: 10;
                   margin-top: 10px;
               }}
           </style>
           <div style="position: relative; margin-bottom: 10px; margin-top: -30px;">
               <div style="text-align: left; margin-bottom: 5px; color: green; font-weight: bold; font-size: 16px; padding-left: 5px;">分數 ({st.session_state["user_score"]} / {len(self.quiz_data)})</div>
               <div class="score-bar-container">
                   <div class="score-bar-fill"></div>
               </div>
           </div>
           """,
           unsafe_allow_html=True,
        )
        st.write("\n")

    # Display the question and answer options
    def display_question_and_answer(self):
        question_item = self.quiz_data[st.session_state["current_question_index"]]
        st.session_state["current_question"] = question_item['question']
        self.start_datetime = datetime.datetime.now()
        self.start_time = time.time()
        if st.session_state["start"] == False:
            st.session_state["remaining_attempts"] = -1
        if st.session_state["remaining_attempts"] == -1:
            st.session_state["remaining_attempts"] = len(question_item['options']) - 1
        if st.session_state["is_answer_submitted"] and st.session_state["selected_option"] == "請選擇一個答案：":
            st.session_state["is_answer_submitted"] = False
            st.error(f"###### {st.session_state['current_question_index'] + 1}. {question_item['question']} (請選擇一個答案！)", icon="⚠️")
        else:
            st.write(f"###### {st.session_state['current_question_index'] + 1}. {question_item['question']}")
        options = question_item['options']
        options.insert(0, "請選擇一個答案：")
        correct_answer = question_item['answer']
        if st.session_state["is_answer_submitted"]:
            st.markdown(
                """
                <style>
                    .nav-buttons-container {
                        margin-top: 50px !important;
                    }
                    @media (prefers-color-scheme: dark) {
                        .nav-buttons-container {
                            background-color: #000000 !important;
                            color: #ffffff !important;
                        }
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            for i, option in enumerate(options):
                if option[0] == correct_answer:
                    if st.session_state["is_answer_correct"]:
                       st.success(fr"{option} (答案正確👍)")
                    else:
                        if st.session_state['remaining_attempts'] > 0:
                            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{option}")
                        else:
                            st.success(fr"{option} (正確答案✔️)")
                elif option == st.session_state["selected_option"]:
                    st.error(fr"{option} (答案不正確❌)")
                elif option != "請選擇一個答案：":
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{option}")
            st.write("\n")
        else:
            st.markdown(
               """
               <style>
                 div[role=radiogroup] label:first-of-type {
                    visibility: hidden;
                    height: 0px;
                 }
                 div[role=radiogroup] label {
                    margin-bottom: 20px;
                 }
                 .stRadio {
                    margin-top: -45px;
                 }
                 @media (prefers-color-scheme: dark) {
                     .stRadio > div {
                         background-color: #000000 !important;
                         color: #ffffff !important;
                     }
                     div[role=radiogroup] label {
                         color: #ffffff !important;
                     }
                 }
               </style>
               """,
               unsafe_allow_html=True,
            )
            st.session_state["selected_option"] = st.radio("請選擇一個答案：", options, label_visibility="hidden")

    # Determine whether 'Next Question', 'Restart', 'Submit' or 'Help' button should be displayed.
    def display_button(self):
        if st.session_state["is_answer_submitted"]:
            with st.container():
                st.markdown('<div class="nav-buttons-container">', unsafe_allow_html=True)
            if st.session_state["current_question_index"] < len(self.quiz_data) - 1:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if not st.session_state["is_answer_correct"] and st.session_state['remaining_attempts'] > 0:
                        st.button('重試🔄', on_click=self.reload_current_question, use_container_width=True)
                    else:
                        st.button('下一題➡️', on_click=self.next_question, use_container_width=True)
                with col2:
                    if not st.session_state["is_answer_correct"] and st.session_state['remaining_attempts'] > 0:
                        st.button('下一題➡️', on_click=self.next_question, use_container_width=True)
                    else:
                        # 移除退出按钮，保持布局但不显示按钮
                        pass
            else:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if not st.session_state["is_answer_correct"] and st.session_state['remaining_attempts'] > 0:
                        st.button('重試🔄', on_click=self.reload_current_question, use_container_width=True)
                    else:
                        st.button('表現分析📊', on_click=self.start_performance_analysis_transition, use_container_width=True)
                with col2:
                    if not st.session_state["is_answer_correct"] and st.session_state['remaining_attempts'] > 0:
                        # 最后一题答错但可重试时，同时显示表现分析按钮
                        st.button('表現分析📊', on_click=self.start_performance_analysis_transition, use_container_width=True)
                    else:
                        # 最后一题答对时，不显示重新开始按钮
                        pass
                if st.session_state["is_answer_correct"] or st.session_state['remaining_attempts'] == 0:
                    # 添加适当的间距，避免覆盖其他内容
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                            margin: 20px 0;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        ">
                            <h2 style="margin: 0; color: white;">🎉 恭喜完成！</h2>
                            <p style="font-size: 18px; margin: 10px 0; color: white;">你已完成所有題目！</p>
                            <p style="font-size: 24px; font-weight: bold; margin: 0; color: #FFD700;">總分：{st.session_state["user_score"]} / {len(self.quiz_data)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <style>
                    .submit-buttons-wrapper {
                        margin-top: -50px !important;
                        padding: 15px;
                        border-radius: 8px;
                        background-color: #ffffff;
                        position: relative;
                        z-index: 1000;
                    }
                    .submit-buttons-wrapper .stButton {
                        margin-top: -35px !important;
                        margin-bottom: 15px !important;
                        transform: translateY(-35px) !important;
                    }
                    .submit-buttons-wrapper .stButton button {
                        margin-right: 50px !important;
                        min-width: 150px !important;
                        white-space: nowrap !important;
                        padding: 8px 16px !important;
                        position: relative !important;
                        z-index: 1001 !important;
                        background-color: #ff6b6b !important;
                        border: 3px solid #ff0000 !important;
                        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5) !important;
                    }
                    .submit-buttons-wrapper .stButton button span {
                        white-space: nowrap !important;
                        display: inline-block !important;
                    }
                    @media (prefers-color-scheme: dark) {
                        .submit-buttons-wrapper {
                            background-color: #000000 !important;
                            color: #ffffff !important;
                        }
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            st.markdown('<div class="submit-buttons-wrapper">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                st.button('提交答案🤲', on_click=self.submit_and_check_answer, use_container_width=True)
            with col2:
                st.button(st.session_state["button_label"], on_click=self.help_clicked, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

