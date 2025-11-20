import time
import base64

import streamlit as st
import mysql

class Auth:
    def __init__(self):
        self.conn = st.connection('mysql', type='sql')
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = 0
        if "logged_key" not in st.session_state:
            st.session_state["logged_key"] = 1
        if "logged_user_name" not in st.session_state:
            st.session_state["logged_user_name"] = ""
    
    def get_logo_base64(self):
        """读取logo.png文件并转换为base64格式"""
        try:
            with open("picture/logo/logo.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
        except Exception as e:
            # 如果读取失败，返回默认的emoji图片
            return ""

    # 登录函数
    def register_page(self):
        # 图片放在页面上方
        st.markdown("""
        <div style='text-align:center;margin-bottom:20px;'>
            <img src='data:image/png;base64,{}' width='250'>
        </div>
        """.format(self.get_logo_base64()), unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        .stDeployButton {display:none !important;}
        [data-testid="stDeployButton"] {display:none !important;}
        .cartoon-input input {
            border-radius: 18px !important;
            border: 2px solid #4fc3f7 !important;
            background: #e1f5fe !important;
            box-shadow: 0 2px 8px #b3e5fc33;
            font-size: 18px;
        }
        .cartoon-btn button {
            border-radius: 18px !important;
            background: linear-gradient(90deg,#4fc3f7,#81d4fa);
            color: #fff !important;
            font-size: 20px;
            font-family: Comic Sans MS,cursive,sans-serif;
            box-shadow: 0 2px 8px #b3e5fc66;
            border: none;
            transition: transform 0.15s;
        }
        .cartoon-btn button:hover {
            transform: scale(1.07) rotate(-2deg);
            background: linear-gradient(90deg,#81d4fa,#4fc3f7);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 使用三列布局居中显示内容
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # 标题在框外
            st.markdown('<h2 style="color:#4fc3f7;font-family:Comic Sans MS,cursive,sans-serif;margin:0;margin-bottom:20px;text-align:center;">用户注册</h2>', unsafe_allow_html=True)
            
            # 使用st.form()创建真正的容器，参考auth.py的做法
            with st.form("register_form", clear_on_submit=False):
                username = st.text_input("👦 用户名", key="login_username", placeholder="请输入用户名", help="支持中英文和数字", label_visibility="visible")
                password = st.text_input("🔑 密码", type="password", key="login_password", placeholder="请输入密码", help="6位及以上", label_visibility="visible")
                class_ = st.number_input("🏫 班级", value=0, step=1, min_value=0, key="login_class")
                
                # 按钮在form内
                col1, col2 = st.columns(2)
                with col1:
                    register_button = st.form_submit_button("🎉 注册", type="primary")
                with col2:
                    login_button = st.form_submit_button("🚪 去登录")
            
            # 处理按钮点击
            if register_button:
                result = self.conn.query(f"SELECT * FROM student_info_25_6 WHERE username = '{username}'")
                if len(result) > 0:
                    st.error("用戶名已存在 😢")
                    time.sleep(2)
                else:
                    mysql.insert_userinfo_data(username, password, class_)
                    st.success("注册成功！🎈")
            
            if login_button:
                self.login_page()
            
            # 额外的按钮在form外
            if st.button("登录"):
                self.login_page()
            if st.button("注册"):
                st.session_state["logged_key"] = 2
                st.rerun()
        # if result == "st":
        #     st.success("登录成功！")
        #     st.session_state['logged_in'] = True
        #     st.session_state['user_id'] = user_id
        #     st.session_state['user_class'] = user_class
        #     print(type(st.session_state['user_class']))
        #     print(st.session_state['user_class'])
        # else:
        #     st.error("登录失败，请检查用户名和密码")
    # def home_page(self):
        # st.title("用户登录")
        # username = st.text_input("请输入用户名")
        # password = st.text_input("请输入密码", type="password")
        # return username, password
        # page = st.sidebar.selectbox("用户页面", ["登录", "注册"])
        # if page == "登录":
        #     self.login_page()
        # else:
        #     self.register_page()
        # if "show_register" not in st.session_state:
        #     st.session_state.show_register = False
        #
        #
        #     # 登录/注册页面切换逻辑
        # if st.session_state.show_register:
        #     self.register_page()
        #     if st.button("← 返回登录"):
        #         st.session_state.show_register = False
        #
        #
        # else:
        #     st.title("用户登录")
        #     # 显示注册链接
        #     col1, col2, col3 = st.columns([1, 1, 1])
        #     with col3:
        #         if st.button("注册新账号 →"):
        #             st.session_state.show_register = True
        #     self.login_page()



    # 用户登录函数
    def login_page(self):
        if st.session_state["logged_key"] == 1:
            # 图片放在页面上方，使用负margin减少间距
            st.markdown("""
        <div style='text-align:center;margin-bottom:0px;margin-top:-100px;display:flex;justify-content:center;align-items:center;'>
            <a href="https://eduhk.au1.qualtrics.com/jfe/form/SV_0DQNvDrgWVBm3iK" target="_blank" style="text-decoration:none;">
                <img src='data:image/png;base64,{}' width='250'>
            </a>
        </div>
        """.format(self.get_logo_base64()), unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            .cartoon-input input {
                border-radius: 18px !important;
                border: 2px solid #ffb300 !important;
                background: #fff8e1 !important;
                box-shadow: 0 2px 8px #ffe08233;
                font-size: 18px;
            }
            .cartoon-btn button {
                border-radius: 18px !important;
                background: linear-gradient(90deg,#ffb300,#ffe082);
                color: #fff !important;
                font-size: 20px;
                font-family: Comic Sans MS,cursive,sans-serif;
                box-shadow: 0 2px 8px #ffe08266;
                border: none;
                transition: transform 0.15s;
            }
            .cartoon-btn button:hover {
                transform: scale(1.07) rotate(2deg);
                background: linear-gradient(90deg,#ffe082,#ffb300);
            }
            /* 强制移动登录表单 */
            div[data-testid="stForm"] {
                margin-top: -50px !important;
                transform: translateY(-10px) !important;
            }
            div[data-testid="column"] {
                margin-top: -50px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 使用三列布局居中显示内容，向上移动减少与logo的距离
            st.markdown('<div style="margin-top:-50px !important; transform: translateY(-10px) !important;">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # 创建登录表单容器
                login_container = st.empty()
                
                # 使用st.form()创建真正的容器，参考auth.py的做法
                with login_container.form("login_form", clear_on_submit=False):
                    username = st.text_input("👦 用戶名", key="login_username2", placeholder="請輸入用戶名", help="支持英文和數字", label_visibility="visible")
                    username = username.lower()
                    password = st.text_input("🔑 密碼", type="password", key="login_password2", placeholder="請輸入密碼", help="6位及以上", label_visibility="visible")
                    password = password.lower()
                    # 按钮占满整个表单宽度
                    login_button = st.form_submit_button("🚪 登錄", type="primary", use_container_width=True)
                
                # 处理按钮点击
                if login_button:
                    # 立即隐藏登录表单
                    login_container.empty()
                    
                    # 执行登录验证
                    print("Login username:", username)
                    print("Login password:", password)
                    result = mysql.check_login(username, password)
                    print("Login result:", result)
                    
                    if result == "student":
                        # 显示成功消息
                        st.success("✅ 登錄成功！正在跳轉到主頁面...")
                        # 清除登录页面状态
                        st.session_state["logged_in"] = 1
                        st.session_state["logged_user_name"] = username
                        st.session_state["logged_key"] = 0
                        # 强制清除页面缓存并重新渲染
                        st.cache_data.clear()
                        st.rerun()
                    elif result == "teacher":
                        # 显示成功消息
                        st.success("✅ 登錄成功！正在跳轉到教師頁面...")
                        # 清除登录页面状态
                        st.session_state["logged_in"] = 2
                        st.session_state["logged_user_name"] = username
                        st.session_state["logged_key"] = 0
                        # 强制清除页面缓存并重新渲染
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        # 显示错误消息
                        st.error("❌ 用戶名或密碼錯誤 😢")
                        time.sleep(1)
                        st.session_state["logged_in"] = 0
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                
                # if register_button:
                #     st.session_state["logged_key"] = 2
                #     st.rerun()
        elif st.session_state["logged_key"] == 2:
            # 图片放在页面上方，使用负margin减少间距
            st.markdown("""
        <div style='text-align:center;margin-bottom:0px;margin-top:-100px;display:flex;justify-content:center;align-items:center;'>
            <img src='data:image/png;base64,{}' width='250'>
        </div>
        """.format(self.get_logo_base64()), unsafe_allow_html=True)
            
            # 使用三列布局居中显示内容，向上移动减少与logo的距离
            st.markdown('<div style="margin-top:-50px !important; transform: translateY(-10px) !important;">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # 标题在框外，使用负margin减少间距
                st.markdown('<h2 style="color:#4fc3f7;font-family:Comic Sans MS,cursive,sans-serif;margin:0;margin-top:-10px;margin-bottom:5px;text-align:center;display:flex;justify-content:center;align-items:center;">用户注册</h2>', unsafe_allow_html=True)
                
                # 使用st.form()创建真正的容器
                with st.form("register_form_inner", clear_on_submit=False):
                    username = st.text_input("👦 用户名", key="register_username", placeholder="请输入用户名", help="支持中英文和数字", label_visibility="visible")
                    password = st.text_input("🔑 密码", type="password", key="register_password", placeholder="请输入密码", help="6位及以上", label_visibility="visible")
                    class_ = st.text_input("🏫 班级", key="register_class", placeholder="请输入班级,如301,501", help="班级编号", label_visibility="visible")
                    sex = st.number_input("👤 性别", min_value=0, max_value=1, value=0, step=1, key="register_sex", help="0代表女，1代表男", label_visibility="visible")
                    
                    # 按钮在form内
                    col1, col2 = st.columns(2)
                    with col1:
                        register_button = st.form_submit_button("🎉 注册", type="primary")
                    with col2:
                        login_button = st.form_submit_button("🚪 去登录")
                
                # 处理按钮点击
                if register_button:
                    # 检查用户名是否已存在
                    result = self.conn.query(f"SELECT * FROM student_info_25_6 WHERE username = '{username}'")
                    if len(result) > 0:
                        st.error("用戶名已存在")
                        time.sleep(2)
                        st.rerun()
                    else:
                        mysql.insert_student_info(username, password, class_, sex)
                        st.success("注册成功")
                        time.sleep(2)
                        st.session_state["logged_key"] = 1
                        st.rerun()
                
                if login_button:
                    st.session_state["logged_key"] = 1
                    st.rerun()
        st.markdown(
            """
            <div style="position: fixed; bottom: 10px; left: 0; right: 0; text-align: center; color: #666; font-size: 14px; white-space: nowrap; z-index: 1000; font-family: 'Times New Roman', 'Georgia', 'Serif', serif;">
                © 2025 Centre for Learning, Teaching and Technology (LTTC), The Education University of Hong Kong. All rights reserved.
            </div>
            """,
            unsafe_allow_html=True
        )