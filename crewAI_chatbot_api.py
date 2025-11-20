import requests
import time
import logging
# from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import os
import ollama
# import Function
import streamlit as st


API_KEY = "Tf20uvnL15rFFb3cdhQ4d4az5u8hVX1c"  # 🔥 替换为你的实际 API Key
COMPLETION_URL = "https://eduhk-api-ea.azure-api.net/ai/v1/completion"
MODEL_NAME = "gpt-4.1"

# Set the location of log file
# log_file_path = os.path.join("log", "crewai_chatbot_api.log")

# # Set the configuration of log file
# logging.basicConfig(
#     handlers=[RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=10, encoding='utf-8')],
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # Initialize the logger
# logger = logging.getLogger()

LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)

def get_user_logger(username):
   
    if not username:
        raise ValueError("Username is required")

    # 清理用户名，防止路径注入（如包含 / 或 \ 等）
    safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_'))[:50]

    log_file_path = os.path.join(LOG_DIR, f"{safe_username}.log")

    # 创建 logger
    logger_name = f"user_logger_{safe_username}"
    logger = logging.getLogger(logger_name)

    # 避免重复添加 handler
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        
        handler = TimedRotatingFileHandler(
            log_file_path,
            when='M',      
            interval=10,   
            backupCount=1,  
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # 防止向上传递到 root logger（避免重复输出）
        logger.propagate = False

    return logger

# Initialize system prompt
SYSTEM = f'''你是一位专业的小学数学教师，现在小学生对一道题目感到疑惑，请你依据指导步骤协助学生完成解答。
注意：
1. 你是一位小学数学教师，而不是AI助手，请以**简练的语言辅导小学生，对话必须简短明了**
2. 即使学生问你的是基础概念，也请你也以最简洁的语言进行讲解
3. 你指导学生的方法包括但不限于鼓励、赞赏、提问、基础概念的讲解以及简单的提示等，如果需要提问，一次尽量只问一个问题
4. **学生如果提出和解题无关的话题，请你设法把话题拉回**
5. 请不要直接告诉学生正确答案，即使是学生强烈要求，作为教师，你必须确保学生在理解的基础上独立完成题目
6. **辅导内容只与当前引导步骤一致,不要提问**
7. 每次输入前，我会将题目与当前引导步骤放在学生的输入前提供给你，请你根据学生输入进行引导
'''

# Set the roles
STUDENT, TEACHER = "user", "assistant"


# Retrieve recent teacher and student dialogues from the conversation history
def retrieve_dialog(history):
    # If an invalid conversation
    if len(history) < 2:
        return None, None
    # If a valid conversation
    else:
        # Verify if the second last entry is from the teacher and if the last entry is from the student
        # if not, return 'empty' dialogues
        if history[-2]["role"] != TEACHER or history[-1]["role"] != STUDENT:
           return None, None
        else:
           teacher_dialog = history[-2]["content"]
           student_dialog = history[-1]["content"]
           return teacher_dialog, student_dialog





def get_llm_response(text="", history=[], header="", system=None):
    # 构建 messages 列表
    messages = []

    if system is not None:
        messages.append({"role": "system", "content": system})

    # 添加对话历史
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})


    content = header + text
    messages.append({"role": "user", "content": content})

    # 请求数据
    data = {
        "model": MODEL_NAME,
        "messages": messages
    }

    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(COMPLETION_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()  # 检查 HTTP 状态码

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            message_content = result["choices"][0]["message"]["content"]
            return message_content.strip()
        else:
            raise Exception("API 返回结果中没有生成有效回复: " + str(result))

    except requests.exceptions.Timeout:
        raise Exception("请求超时，请重试。")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except KeyError as e:
        raise Exception(f"响应数据格式错误，缺少字段: {str(e)}")


def get_llm_feedback(text="", model=MODEL_NAME):
    content = text
    messages = [{"role": "user", "content": content}]

    # 请求数据
    data = {
        "model": model,
        "messages": messages
    }

    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(COMPLETION_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()  # 检查 HTTP 状态码

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            message_content = result["choices"][0]["message"]["content"]
            return message_content.strip()
        else:
            raise Exception("API 返回结果中没有生成有效回复: " + str(result))

    except requests.exceptions.Timeout:
        raise Exception("请求超时，请重试。")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except KeyError as e:
        raise Exception(f"响应数据格式错误，缺少字段: {str(e)}")

# Check if the explanation is answered by student from the check_messages
def agent_check_is_explanation_answered(check_messages, explanation):
    start_time = time.time()
    conversation = ""
    for h in check_messages:
        if h['role'] == 'user':
            conversation += f"学生: {h['content']}\n"
        else:
            conversation += f"教师: {h['content']}\n"
    prompt = f'''以请你基于以下对话判断学生是否有对当前引导步骤做出回答：
## 注意：
1. 只需要判断学生是否对**当前引导步骤**做出了明确回答，不要受到老师提问的干扰， **当前引导步骤**我会在下面提供给你
2. 如果学生提出疑问则视为【有回答】
3. 请以尽量简短的话语来进行逐步思考，不要太过冗长并在**最后生成【无回答】或【有回答】**


### 当前引导步骤
{explanation}
### 对话
{conversation}
'''
    # Ask LLM for response
    response = get_llm_feedback(text=prompt)
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    logger.info(f'''====LLM checking if a analysis is answered====
【prompt】
{prompt}
【response】
{response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    print("是否回答的判断：" + response)
    return "有回答" in response[-10:]  # return whether the string "有回答" is present in the response (True or False)

# Check whether to move to the next explanation step
def agent_check_move_to_next_explanation(question, explanation, scale, check_messages):
    conversation = ""
    messages = []
    start_time = time.time()
    for h in check_messages:
        if h['role'] == 'user':
            conversation += f"学生: {h['content']}\n"
        else:
            conversation += f"教师: {h['content']}\n"
    content = f'''以下是题目，当前引导以及教师与学生的对话，请逐步思考，然后根据评判标准判断学生是否掌握当前引导,**最后生成【已掌握】或【未掌握】**：
## 注意：
1. 你不需要解题，请以尽量简短的话语来进行逐步思考，不要太过冗长
2. 题目，当前引导步骤，评判标准和对话我会在下面提供给你
3. 你需要根据对话找到学生对当前引导步骤的回答，然后根据评判标准判断学生是否掌握
4. 当学生的回答不完全正确时，**你只需要根据判断标准判断当前引导步骤中的问题是否回答掌握**，
5. 如果学生未回答当前引导步骤时说明未掌握
6. 当学生提出疑问时，则说明未掌握

### 题目
{question}
### 当前引导步骤
{explanation}
### 评判标准
{scale}
### 对话
{conversation}
'''
    content = content
    # messages.append({'role': 'user', 'content': content})
    # response = ollama.chat(
    #     model=model,
    #     messages=messages,
    #     stream=False,
    # )
    response = get_llm_feedback(text=content)
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    # response = response['message']['content']
    logger.info(f'''====LLM checking about explanation ====
        【prompt】
        {content}
        【response】
        {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    # part = response.split("</think>\n\n", 1)
    # response = part[1]
    print("是否掌握的判断：" + response)
    return "已掌握" in response[-10:]


# Check if a teacher question is answered by student from the conversation history
def agent_check_is_question_answered(history):
    teacher_dialog, student_dialog = retrieve_dialog(history)
    start_time = time.time()
    if teacher_dialog == None or student_dialog == None:
        return None
    prompt = f'''以请你基于以下对话判断学生是否有对老师的提问做出回答：
## 注意：
1. **请只输出【无回答】或【有回答】，除此以外不需要任何额外内容**
2. 如果老师没有进行提问，请直接视为【无回答】
3. 只需要判断学生是否回答，请无视无视其他操作

### 教师
{teacher_dialog}
### 学生
{student_dialog}
'''
    # Ask LLM for response
    response = get_llm_feedback(text=prompt)
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    logger.info(f'''====LLM's checking whether a question is answered====
【prompt】
{prompt}
【response】
{response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    return "有回答" in response     # return whether the string "有回答" is present in the response (True or False)


# Error Tutor 你只需要以教师的口吻输出辅导，不要输出其他
def agent_error_tutor(question, history):
    teacher_dialog, student_dialog = retrieve_dialog(history)
    start_time = time.time()
    prompt = f'''以请你基于以下老师与学生的对话，对学生的错误进行辅导：
## 注意：
1. **学生的回答一定是错误的！请你先找到学生的错误！**
2. **你不需要解题，只要对学生当前的错误回答进行辅导，语言要简单明了**
3. 你是一位小学数学教师，而不是AI助手，请以**简练的语言辅导小学生，对话必须简短明了**

### 题目
{question}
### 教师
{teacher_dialog}
### 学生
{student_dialog}
'''
    # Ask LLM for response
    response = get_llm_feedback(text=prompt)
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    logger.info(f'''====Error Tutor====
    【prompt】
    {prompt}
    【response】
    {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    # part = response.split("</think>\n\n", 1)
    # response = part[1]
    print("纠错助手输出：" + response)
    return response

# Check if student answer to teacher question is correct from the conversation history
def agent_check_is_incorrect_answer(history, question):
    teacher_dialog, student_dialog = retrieve_dialog(history)
    start_time = time.time()
    # if "lcm" in st.session_state and st.session_state["lcm"]:
    # numbers = []
    # for element in st.session_state["lcm"]:
    #     numbers.append(element["denominator"])
    #
    # result = Function.LCM(numbers)
    # output = '分母' + ','.join(
    #     str(x) for x in numbers) + f"的最小公倍数是{result}，通分后的分母也应该是{result}，其他回答均错误！" 1. **{output}**
    if teacher_dialog == None or student_dialog == None:
        return None
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    prompt = f'''以下是题目和教师与学生的对话，请你逐步思考，再判断学生的回答是否正确，**最后生成【正确】或【不正确】**
## 注意：
1. 请以尽量简短的话语来进行逐步思考，不要太过冗长
2. 请在结尾生成【正确】或【不正确】
3. **你不需要去解题，只要判断学生的回答对于老师当前的提问是否正确**


### 题目
{question}
### 教师
{teacher_dialog}
### 学生
{student_dialog}
'''
    response = get_llm_feedback(text=prompt)
    logger.info(f'''====LLM checking if an answer is incorrect====
    【prompt】
    {prompt}
    【response】
    {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    # part = response.split("</think>\n\n", 1)
    # response = part[1]
    print("是否正确的判断：" + response)
    return "不正确" in response[
                       -10:]  # return whether the string "不正確" is present in the last part of response (True or False)


def agent_tutor(user_input, question, explanation, history):
    system = SYSTEM
    history.append({"role": "user", "content": user_input})
    header = ""
    # Check if a valid conversation history (i.e. with a minimum length of 2)
    if len(history) >= 2:
        is_incorrect_answer = agent_check_is_incorrect_answer(history, question)  # Check if the answer is incorrect
        # if the answer is incorrect
        if is_incorrect_answer != None and is_incorrect_answer:
            result = agent_error_tutor(question, history)
            history.append({"role": "assistant", "content": result})

            return history, result

    start_time = time.time()
    header += f'''## 题目
{question}
## 当前引导步骤
{explanation}
## 学生输入\n
'''
    response = get_llm_response(user_input, history[:-1], header, system)
    history.append({"role": "assistant", "content": response})
    username = st.session_state.get("logged_user_name")
    logger = get_user_logger(username)
    logger.info(f'''====LLM response on step-by-step guidance====
    【prompt】
    {header + user_input}
    【response】
    {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to} s  {len(response) / to} words/s")
    # st.session_state.messages_with_error = ''
    return history, response



