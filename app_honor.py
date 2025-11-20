import streamlit as st

import mysql
from home_honor import Auth
from quiz_honor import Quiz
from chatbot_voice_9_18 import Chatbot
from PIL import Image
import os
import base64

# set_page_config 必须是第一个Streamlit命令
st.set_page_config(
    page_title="分數練習",  # 可根据需要自定义
    page_icon="picture/logo/logo_small.png",    # 自定义favicon]
)


if 'sidebar_state' not in st.session_state:
    st.session_state["sidebar_state"] = 'collapsed'  # Initialize sidebar state
    initial_sidebar_state = st.session_state["sidebar_state"]

# UI美化和兼容性增强CSS/JS（合并原app.py的全部样式）
hide_sidebar_button_css = """
<style>
    [data-testid="stBaseButton-headerNoPadding"] {
        display: none;  /* Hides the sidebar collapse button */
    }
    
    /* Make LaTeX fractions larger throughout the app */
    .katex {
        font-size: 1.5em !important;
    }
    .katex-display {
        font-size: 1.5em !important;
    }
    /* Target specific fraction elements */
    .katex .frac-line {
        font-size: 1.5em !important;
    }
    .katex .frac-num {
        font-size: 1.5em !important;
    }
    .katex .frac-den {
        font-size: 1.5em !important;
    }
    
    /* Reduce main content margins for more screen space */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Reduce spacing between elements */
    .stSelectbox, .stRadio, .stButton, .stTextInput {
        margin-bottom: 0.5rem;
    }
    
    /* Reduce header margins */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Reduce paragraph margins */
    p {
        margin-bottom: 0.5rem;
    }
    
    /* Reduce container padding */
    .stContainer {
        padding: 0.5rem;
    }
    
    /* Make the app use more of the available width */
    .reportview-container .main .block-container {
        max-width: 95%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Reduce space between title and selectbox */
    .stSelectbox {
        margin-top: -20px;
    }
    
    /* 移动进度条到更高位置 */
    .car-progress-container {
        margin-top: -20px !important;
        transform: translateY(-10px) !important;
    }
    
    /* 移动提交答案和提示按钮到更高位置 */
    .stButton {
        margin-top: -25px !important;
        transform: translateY(-10px) !important;
    }
    
    div[data-testid="column"] .stButton {
        margin-top: -25px !important;
        transform: translateY(-10px) !important;
    }
    
    
</style>

"""
st.markdown(hide_sidebar_button_css, unsafe_allow_html=True)


if 'button_label' not in st.session_state:
    st.session_state["button_label"] = '開啟幫手🤖'  # Initialize help button label

if 'show_performance_analysis' not in st.session_state:
    st.session_state["show_performance_analysis"] = False  # Initialize performance analysis display state


# Load the app page
def page():
    # 创建页面容器来管理页面切换
    page_container = st.empty()
    
    # create chatbot
    if "chatbot" not in st.session_state:
        st.session_state["chatbot"] = Chatbot()
    if "auth" not in st.session_state:
        st.session_state["auth"] = Auth()
    if "start" not in st.session_state:
        st.session_state["start"] = False

    # check if login successfully
    # if st.session_state["auth"].check_login():
    #     st.session_state["auth"].login_success_page()
    if st.session_state["logged_in"] == 1:
        # Check if logout transition is in progress
        if st.session_state.get("logout_transition", False):
            # Clear page container and show only logout message
            page_container.empty()
            
            # Clear all session state first
            st.session_state["logged_user_name"] = ""
            st.session_state["logged_in"] = 0
            st.session_state["logged_key"] = 1
            st.session_state["show_performance_analysis"] = False
            st.session_state["user_score"] = 0
            st.session_state["current_question_index"] = 0
            st.session_state["selected_quiz_from_right"] = ""
            st.session_state["sidebar_state"] = "collapsed"
            st.session_state["chatbot"] = Chatbot()
            st.session_state["auth"] = Auth()
            # Clear quiz related states
            st.session_state["is_answer_submitted"] = False
            st.session_state["start"] = False
            st.session_state["selected_option"] = None
            st.session_state["remaining_attempts"] = -1
            st.session_state["current_question"] = []
            st.session_state["current_explanation_index"] = 0
            st.session_state["current_explanations"] = []
            st.session_state["denominators"] = []
            st.session_state["is_answer_correct"] = False
            st.session_state["prompt"] = []
            st.session_state["is_first_user_prompt"] = True
            st.session_state["messages_cn"] = []
            st.session_state["messages_tw"] = []
            st.session_state["competence_domains"] = {}
            st.session_state["error_domains"] = {}
            st.session_state["button_label"] = "開啟幫手🤖"
            st.session_state["data_fig"] = None
            st.session_state["lcm"] = None
            st.session_state["check_messages"] = []
            st.session_state["logout_transition"] = False
            
            # Show only logout message
            st.markdown("""
            <style>
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }
            .logout-icon {
                animation: bounce 2s infinite;
                font-size: 3rem;
                margin-bottom: 20px;
            }
            </style>
            <div style='text-align:center; margin-top: 15vh;'>
                <div class='logout-icon'>🚪</div>
                <h2>已登出</h2>
                <p>正在返回登入頁面...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Small delay then rerun to show login screen
            import time
            time.sleep(1)
            st.rerun()
            return
        
        # Check if performance analysis transition is in progress
        if st.session_state.get("performance_analysis_transition", False):
            # Clear page container and show only transition message
            page_container.empty()
            
            # Show only transition message
            st.markdown("""
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-spinner {
                display: inline-block;
                width: 30px;
                height: 30px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 15px;
                vertical-align: middle;
            }
            </style>
            <div style='text-align:center; margin-top: 10vh;'>
                <h2><span class="loading-spinner"></span>正在生成分析中...</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Small delay then proceed to performance analysis
            import time
            time.sleep(2)
            st.session_state["performance_analysis_transition"] = False
            st.session_state["show_performance_analysis"] = True
            st.session_state["show_performance_analysis_ready"] = True  # Set flag to skip the first-time wait in quiz_honor
            st.rerun()
            return
        
        # 使用容器管理主页面内容
        with page_container.container():
            st.session_state["user_input"] = ""
            
            # 添加图片到页面上方
            auth = Auth()
            # Create logo container with logout button
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown("""
                <div style='text-align:center;margin-bottom:20px;margin-top:-90px;display:flex;justify-content:center;align-items:center;margin-left:80px;'>
                    <img src='data:image/png;base64,{}' width='150'>
                </div>
                """.format(auth.get_logo_base64()), unsafe_allow_html=True)
            with col2:
                st.markdown('<div style="margin-top:-140px;">', unsafe_allow_html=True)
                if st.button("🚪 登出", key="logout_button", type="secondary"):
                    # Set logout transition flag
                    st.session_state["logout_transition"] = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 只在非表现分析页面显示"選擇題庫"文本
            if not st.session_state["show_performance_analysis"]:
                st.markdown("""
                <div style='margin-top:-60px;text-align:left;'>
                    <div style='color:#0066cc;font-weight:bold;margin-bottom:5px;'>選擇題庫</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 选择题库区域 - 在logo下方，主要内容上方
            quiz_file_names = ["同分母分數比較大小", "同分子分數比較大小", "等值分數的概念", "基本分數加減法概念：同分母加減法", "公倍數", "公因數", "擴分", "約分", 
            "假分數與帶分數互化", "分數加法：將滿一的分數部分進到整數部分", "分數減法：分數部分不夠減時向整數部分借", 
            "兩個異分母分數加法", "三個異分母分數加法", "兩個異分母分數減法", "三個異分母分數減法", "三個異分母分數加減混合"]
            # quiz_file_names = ["擴分", "等值分數的概念"]
            # 从右侧获取选择的题库
            if "selected_quiz_from_right" in st.session_state:
                selected_quiz_file_name = st.session_state["selected_quiz_from_right"]
            else:
                selected_quiz_file_name = quiz_file_names[0]
            
            # 选择题库下拉菜单 - 直接在logo下方，左对齐（只在非表现分析页面显示）
            if not st.session_state["show_performance_analysis"]:
                st.markdown("""
                <style>
                div[data-testid="stSelectbox"] {
                    margin-top: -70px !important;
                    transform: translateY(-15px) !important;
                }
                </style>
                """, unsafe_allow_html=True)
                st.markdown('<div style="margin-top:-50px;text-align:left;">', unsafe_allow_html=True)
                if not st.session_state["start"]:
                    selected_quiz_file_name_main = st.selectbox("选择题库", quiz_file_names, key="quiz_select_main", label_visibility="collapsed", index=quiz_file_names.index(selected_quiz_file_name) if selected_quiz_file_name in quiz_file_names else 0)
                    
                    # 更新session state
                    if selected_quiz_file_name_main != selected_quiz_file_name:
                        st.session_state["selected_quiz_from_right"] = selected_quiz_file_name_main
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # 显示锁定的选择题库下拉菜单，显示当前选中的项目但不可更改
                    st.selectbox("选择题库", quiz_file_names, key="quiz_select_locked", label_visibility="collapsed", 
                               index=quiz_file_names.index(selected_quiz_file_name) if selected_quiz_file_name in quiz_file_names else 0,
                               disabled=True)
            
            # 进度条显示在主窗口，列布局之外
            if selected_quiz_file_name:
                q = Quiz(selected_quiz_file_name)
                q.load_quiz()
                
                # 显示进度条在主窗口
                if not st.session_state["show_performance_analysis"]:
                    st.markdown("""
                    <style>
                    .car-progress-container {
                        margin-top: -45px !important;
                        transform: translateY(-25px) !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    q.display_progress_and_score()
            
            # display quiz in the main window
            if selected_quiz_file_name:
                # show the performance analysis
                if st.session_state["show_performance_analysis"]:
                    # 表现分析页面：移除列布局，内容居中对齐
                    st.markdown("""
                    <div style='text-align: center; width: 100%;'>
                    """, unsafe_allow_html=True)
                    q.display_performance_analysis()
                    st.markdown("""
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 正常答题页面：移除列布局，让组件直接显示
                    # 主要内容区域
                    q.display_question_and_answer()
                    q.display_button()
            
            # 恢复sidebar渲染机器人对话区
            st.markdown("""
            <style>
            section[data-testid="stSidebar"] {
                width: 35% !important;
            }
            section[data-testid="stSidebar"] h3 {
                margin: -10px 0 10px 0 !important;
                padding-top: 0 !important;
            }
            section[data-testid="stSidebar"] .block-container {
                padding-top: 0.5rem !important;
            }
            /* 侧边栏radio样式优化 */
            section[data-testid="stSidebar"] .stRadio > label { margin-top: 50px; }
            div[role=radiogroup] label:first-of-type {
                visibility: hidden;
                height: 0;
            }
            div[role=radiogroup] label { margin-bottom: 20px; }
            .stRadio { margin-top: -60px; }
            </style>
            """, unsafe_allow_html=True)
            with st.sidebar:
                if st.session_state["sidebar_state"] == "expanded":
                    title_container = st.container()
                    with title_container:
                        st.subheader("輔導機械人🤖")
                    if st.session_state["sidebar_state"] == "expanded":
                        content_container = st.container()
                        with content_container:
                            if st.session_state["chatbot"] is not None:
                                st.session_state["chatbot"].display_messages(in_sidebar=True)

            st.markdown("""
                  <style>
                  @keyframes arrow-flash {
                      0%, 100% { opacity: 1; transform: translateY(0); }
                      50% { opacity: 0.35; transform: translateY(8px); }
                  }
                  .arrow-flash {
                      display: inline-flex;
                      gap: 4px;
                      margin-left: 8px;
                  }
                  .arrow-flash span {
                      display: inline-block;
                      animation: arrow-flash 1.2s infinite ease-in-out;
                  }
                  .arrow-flash span:nth-child(2) { animation-delay: 0.15s; }
                  .arrow-flash span:nth-child(3) { animation-delay: 0.3s; }
                  </style>
                """, unsafe_allow_html=True)
            
            if st.session_state["sidebar_state"] == "expanded":
                with st.container():
                    try:
                        if st.session_state["current_num_solutions"] == 1:
                            num = st.session_state["current_explanation_index"] + 1
                            image_path = f'D:/SZX/Picture/{selected_quiz_file_name}/{st.session_state["current_question_index"]}_{num}.jpg'
                            if os.path.exists(image_path):  # 检查文件是否存在
                                image_a = Image.open(image_path)
                                st.image(image_a, use_column_width=True)

                        else:
                            num = st.session_state["current_explanation_index"] + 1
                            image_path = f'D:/SZX/Picture/{selected_quiz_file_name}/{st.session_state["current_question_index"]}_{st.session_state["current_choice"]}_{num}.jpg'
                            if os.path.exists(image_path):  # 检查文件是否存在
                                image_a = Image.open(image_path)
                                st.image(image_a, use_column_width=True)
                    except Exception as e:
                        pass
                        # st.warning(f"图片加载失败: {e}")  # 可选：显示错误信息

                # st.markdown("""
                #   <style>
                #   @keyframes arrow-flash {
                #       0%, 100% { opacity: 1; transform: translateY(0); }
                #       50% { opacity: 0.35; transform: translateY(8px); }
                #   }
                #   .arrow-flash {
                #       display: inline-flex;
                #       gap: 4px;
                #       margin-left: 8px;
                #   }
                #   .arrow-flash span {
                #       display: inline-block;
                #       animation: arrow-flash 1.2s infinite ease-in-out;
                #   }
                #   .arrow-flash span:nth-child(2) { animation-delay: 0.15s; }
                #   .arrow-flash span:nth-child(3) { animation-delay: 0.3s; }
                #   </style>
                # """, unsafe_allow_html=True)

                with st.container():
                    if st.session_state["data_fig"] and st.session_state.get("remaining_attempts", -1) > 0:
                        # 添加适当的间距
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("""
                        <div style="margin-top: -50px;">
                            <h3>📊 題目分數示意圖 <span class="arrow-flash"><span>⬇️</span><span>⬇️</span><span>⬇️</span></span></h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.pyplot(st.session_state["data_fig"], use_container_width=True)
                        st.markdown("<div style='text-align: center; font-weight: bold;'>💡 點擊右側按鈕可全屏查看圖片或退出全屏</div>", unsafe_allow_html=True)
            
            # 在主界面显示最终图，当用尽尝试次数时
            if (st.session_state.get("data_fig") and 
                st.session_state.get("is_answer_submitted", False) and 
                st.session_state.get("remaining_attempts", -1) <= 0):
                # 添加适当的间距，避免与完成消息重叠
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("""
                <div style="margin-top: -50px;">
                    <h3>📊 答案分數示意圖 <span class="arrow-flash"><span>⬇️</span><span>⬇️</span><span>⬇️</span></span></h3>
                </div>
                """, unsafe_allow_html=True)
                st.pyplot(st.session_state["data_fig"], use_container_width=True)
                st.markdown("<div style='text-align: center; font-weight: bold;'>💡 點擊右側按鈕可全屏查看圖片或退出全屏</div>", unsafe_allow_html=True)
    elif st.session_state["logged_in"] == 2:
        # 使用容器管理教师页面内容
        with page_container.container():
            st.markdown("""
            <style>
            .center-title {text-align:center; font-size:2rem; font-weight:bold; margin-bottom:1.5rem;}
            .section-title {font-size:1.2rem; font-weight:bold; color:#2a5d9f; background:#eaf1fb; padding:8px 16px; border-radius:8px; margin:18px 0 8px 0;}
            .stRadio > label {font-weight:bold;}
            .stDataFrame th, .stDataFrame td {text-align:center !important;}
            .stDataFrame table {border-collapse:collapse;}
            .stDataFrame td, .stDataFrame th {border:1px solid #e0e0e0;}
            .stDataFrame {background:#fcfcfc; border-radius:8px;}
            .stInfo {margin:10px 0;}
            </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="center-title">👩‍🏫 教師數據總覽</div>', unsafe_allow_html=True)
            st.markdown("---")
            col1, col2 = st.columns(2)
            username = st.session_state.get("logged_user_name", "")
            # 左侧
            with col1:
                st.markdown('<div class="section-title">📚 按班級進行查看</div>', unsafe_allow_html=True)
                teacher_classes = mysql.get_teacher_classes(username)
                if teacher_classes:
                    import pandas as pd
                    selected_class = st.radio("\n請選擇要查看的班級：", teacher_classes, key="radio_class")
                    if selected_class:
                        c = selected_class
                        students = mysql.get_students_by_class(c)
                        chatbot_data = mysql.select_chatbot_data()
                        choice_data = mysql.select_choice_data()
                        class_chatbot = [row for row in chatbot_data if row[1] in students]
                        class_choice = [row for row in choice_data if row[1] in students]
                        st.markdown('<div class="section-title">🤖 AI使用情况</div>', unsafe_allow_html=True)
                        if class_chatbot:
                            chatbot_df = pd.DataFrame(class_chatbot, columns=["id","用戶名","題庫","題目id","使用時間"])
                            chatbot_df = chatbot_df.drop(columns=["id"])
                            st.dataframe(chatbot_df, use_container_width=True)
                        else:
                            st.info("該班暫無AI使用記錄", icon="ℹ️")
                        st.markdown('<div class="section-title">📝 作答情況</div>', unsafe_allow_html=True)
                        if class_choice:
                            choice_df = pd.DataFrame(class_choice, columns=["id","用戶名","題庫","題目id","學生回答","正確答案","聊天機器人狀態","作答時間"])
                            choice_df = choice_df.drop(columns=["id"])
                            st.dataframe(choice_df, use_container_width=True)
                        else:
                            st.info("該班暫無作答記錄", icon="ℹ️")
                else:
                    st.info("未查到教師班級信息", icon="ℹ️")
            # 右侧
            with col2:
                st.markdown('<div class="section-title">🔍 按題庫和題目查看</div>', unsafe_allow_html=True)
                teacher_classes = mysql.get_teacher_classes(username)
                students = mysql.get_students_by_classes(teacher_classes) if teacher_classes else []
                if students:
                    choice_data = mysql.select_choice_data()
                    chatbot_data = mysql.select_chatbot_data()
                    filtered_choice = [row for row in choice_data if row[1] in students]
                    filtered_chatbot = [row for row in chatbot_data if row[1] in students]
                    question_banks = sorted(list(set([row[2] for row in filtered_choice])))
                    selected_bank = st.radio("\n請選擇題庫：", question_banks, key="radio_bank") if question_banks else None
                    if selected_bank:
                        bank_choices = [row for row in filtered_choice if row[2] == selected_bank]
                        bank_chatbot = [row for row in filtered_chatbot if row[2] == selected_bank]
                        question_ids = sorted(list(set([row[3] for row in bank_choices])))
                        selected_qid = st.radio(f"題庫 {selected_bank} 的題目id：", question_ids, key="radio_qid") if question_ids else None
                        if selected_qid:
                            q_choices = [row for row in bank_choices if str(row[3]) == str(selected_qid)]
                            q_chatbot = [row for row in bank_chatbot if str(row[3]) == str(selected_qid)]
                            st.markdown('<div class="section-title">🤖 AI使用情况</div>', unsafe_allow_html=True)
                            if q_chatbot:
                                import pandas as pd
                                chatbot_df = pd.DataFrame(q_chatbot, columns=["id","用戶名","題庫","題目id","使用時間"])
                                chatbot_df = chatbot_df.drop(columns=["id"])
                                st.dataframe(chatbot_df, use_container_width=True)
                            else:
                                st.info("該題暫無AI使用記錄", icon="ℹ️")
                            st.markdown('<div class="section-title">📝 作答情况</div>', unsafe_allow_html=True)
                            if q_choices:
                                import pandas as pd
                                choice_df = pd.DataFrame(q_choices, columns=["id","用戶名","題庫","題目id","學生回答","正確答案","聊天機器人狀態","作答時間"])
                                choice_df = choice_df.drop(columns=["id"])
                                st.dataframe(choice_df, use_container_width=True)
                            else:
                                st.info("該題暫無作答記錄", icon="ℹ️")
                else:
                    st.info("未查到本教師班級學生", icon="ℹ️")
            st.markdown("---")
            # 新增：学生作答与AI使用情况搜索
            st.markdown('<div class="section-title">🔎 按學生賬號查找</div>', unsafe_allow_html=True)
            search_username = st.text_input("請輸入學生用戶名進行查詢：", key="search_username")
            if st.button("搜索", key="search_btn"):
                if search_username:
                    stu_class = mysql.get_student_class(search_username)
                    teacher_classes = mysql.get_teacher_classes(username)
                    if stu_class and stu_class in teacher_classes:
                        chatbot_data = mysql.select_chatbot_data()
                        choice_data = mysql.select_choice_data()
                        stu_chatbot = [row for row in chatbot_data if row[1] == search_username]
                        stu_choice = [row for row in choice_data if row[1] == search_username]
                        st.markdown('<div class="section-title">🤖 AI使用情况</div>', unsafe_allow_html=True)
                        if stu_chatbot:
                            import pandas as pd
                            chatbot_df = pd.DataFrame(stu_chatbot, columns=["id","用戶名","題庫","題目id","使用時間"])
                            chatbot_df = chatbot_df.drop(columns=["id"])
                            st.dataframe(chatbot_df, use_container_width=True)
                        else:
                            st.info("该学生暂无AI使用记录", icon="ℹ️")
                        st.markdown('<div class="section-title">📝 作答情况</div>', unsafe_allow_html=True)
                        if stu_choice:
                            import pandas as pd
                            choice_df = pd.DataFrame(stu_choice, columns=["id","用戶名","題庫","題目id","學生回答","正確答案","聊天機器人狀態","作答時間"])
                            choice_df = choice_df.drop(columns=["id"])
                            st.dataframe(choice_df, use_container_width=True)
                        else:
                            st.info("該學生暫無作答記錄", icon="ℹ️")
                    else:
                        st.warning("該學生不屬於您的班級，無法查詢！")
                else:
                    st.warning("請輸入學生用戶名後再查找！")

    else:
        # 使用容器管理登录页面内容
        with page_container.container():
            st.session_state["auth"].login_page()
    
    # Check if rerun is needed for transitions
    if st.session_state.get("performance_analysis_transition", False) or st.session_state.get("logout_transition", False):
        st.rerun()


# Start the app with page()
if __name__ == "__main__":
    page()

