import streamlit as st
import time
import logging
from logging.handlers import RotatingFileHandler
import os
import ollama
from translator import translate_tw
import asyncio
import Function

# Set the location of log file
log_file_path = os.path.join("log", "chat-math.log")

# Set the configuration of log file
logging.basicConfig(
    handlers=[RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=10, encoding='utf-8')],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize the logger
logger = logging.getLogger()

# Initialize system prompt
SYSTEM = f'''你是一位专业的小学数学教师，现在小学生对一道题目感到疑惑，请你依据指导步骤协助学生完成解答。
注意：
你是一位小学数学教师，而不是AI助手，请以**简练的语言辅导小学生，对话必须简短明了**
2. 即使学生问你的是基础概念，也请你也以最简洁的语言进行讲解
3. 你指导学生的方法包括但不限于鼓励、赞赏、提问、基础概念的讲解以及简单的提示等，如果需要提问，一次尽量只问一个问题
4. **学生如果提出和解题无关的话题，请你设法把话题拉回**
5. 请不要直接告诉学生正确答案，即使是学生强烈要求，作为教师，你必须确保学生在理解的基础上独立完成题目
6. **辅导内容只与当前引导步骤一致,不要提问**
7. 每次输入前，我会将题目与当前引导步骤放在学生的输入前提供给你，请你根据学生输入进行引导
'''

# Set the roles
STUDENT, TEACHER = "user", "assistant"

# A function to translate simplified Chinese to traditional Chinese
def sync_translate_tw(text):
    return asyncio.run(translate_tw(text))


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


# Remove <think>...</think> from deepseek's response
def format_deepseek_response(response):
    part = response.split("</think>\n\n", 1)
    return part[1]   


# Get the response from LLM, based on the conversation history and the user prompt
def get_llm_feedback_with_history(prompt="", history=[], header="", model="qwen2.5", system=None):
    if system == None:
        messages = []
        content = header + prompt
    else:
        messages = [{'role': 'system', 'content': system}]
        content = header + prompt
    if len(history) > 0:
        for h in history:
            messages.append({'role': h['role'], 'content': h['content']})    
    messages.append({'role': 'user', 'content': content})
    completion = ollama.chat(
        model=model,
        messages=messages,
        stream=False,
    )
    return completion['message']['content']


# Get the response from LLM, mainly based on the prompt given (i.e. text)
def get_llm_feedback_without_history(prompt="",model="deepseek-r1:14b"):
    content = prompt
    messages = []

    messages.append({'role': 'user', 'content': content})
    completion = ollama.chat(
        model=model,
        messages=messages,
        stream=False,
    )
    if model == "deepseek-r1:14b":
       return format_deepseek_response(completion['message']['content'])
    else:
       return completion['message']['content']


# Check the conversation history to see if the guidance question is answered by the student
def check_guidance_question_answered(check_messages, guidance_step):
    start_time = time.time()
    conversation = ""
    for h in check_messages:
        if h['role'] == 'user':
            conversation += f"学生: {h['content']}\n"
        else:
            conversation += f"教师: {h['content']}\n"
    prompt = f'''以请你基于以下对话判断学生是否有对当前引导步骤做出回答：
## 注意：
只需要判断学生是否对**当前引导步骤**做出了明确回答，不要受到老师提问的干扰， **当前引导步骤**我会在下面提供给你
2. 如果学生提出疑问则视为【有回答】
3. 请以尽量简短的话语来进行逐步思考，不要太过冗长并在**最后生成【无回答】或【有回答】**

### 当前引导步骤
{guidance_step}
### 对话
{conversation}
'''
    # Ask LLM for response
    model = "deepseek-r1:14b"
    response = get_llm_feedback_without_history(prompt, model)
    logger.info(f'''<<< LLM's checking whether the current guidance question is answered >>>
               【prompt】
                {prompt}
               【response】
                {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    print("是否回答的判断：" + response + '\n')
    return "有回答" in response[-10:]  # return whether the string "有回答" is present in the response (True or False)


# Check whether to move to the next guidance step
def check_move_to_next_guidance_step(question, guidance_step, passing_condition, check_messages, model="deepseek-r1:14b"):
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
你不需要解题，请以尽量简短的话语来进行逐步思考，不要太过冗长
2. 题目，当前引导步骤，评判标准和对话我会在下面提供给你
3. 你需要根据对话找到学生对当前引导步骤的回答，然后根据评判标准判断学生是否掌握
4. 当学生的回答不完全正确时，**你只需要根据判断标准判断当前引导步骤中的问题是否回答掌握**，
5. 如果学生未回答当前引导步骤时说明未掌握
6. 当学生提出疑问时，则说明未掌握

### 题目
{question}
### 当前引导步骤
{guidance_step}
### 评判标准
{passing_condition}
### 对话
{conversation}
'''
    messages.append({'role': 'user', 'content': content})
    response = ollama.chat(
        model= model,
        messages= messages,
        stream= False,
    )
    response = response['message']['content']
    logger.info(f'''<<< LLM's checking whether the student understands the current guidance step >>>
               【prompt】
                {content}
               【response】
                {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    if model == "deepseek-r1:14b":
       #print(response)
       response = format_deepseek_response(response)
    print("是否掌握的判断：" + guidance_step + response + '\n')
    return "已掌握" in response[-10:]  # return whether the string "已掌握" is present in the response (True or False)


# Offer tutoring to correct student error
def tutoring_for_student_error(question, history):
    teacher_dialog, student_dialog = retrieve_dialog(history)
    start_time = time.time()
    prompt = f'''以请你基于以下老师与学生的对话，对学生的错误进行辅导：
## 注意：
**学生的回答一定是错误的！请你先找到学生的错误！**
2. **你不需要解题，只要对学生当前的错误回答进行辅导，语言要简单明了**
3. 你只需要以教师的口吻输出辅导，不要输出其他

### 题目
{question}
### 教师
{teacher_dialog}
### 学生
{student_dialog}
'''
    # Ask LLM for response
    model = "deepseek-r1:14b"
    response = get_llm_feedback_without_history(prompt, model)
    logger.info(f'''<<< LLM's tutoring to correct student error >>>
               【prompt】
                {prompt}
               【response】
                {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    print("糾錯助手輸出：" + response)
    return response


# Check from conversation history to see if student answer to guidance question is incorrect
def check_student_incorrect_answer(history, question):
    teacher_dialog, student_dialog = retrieve_dialog(history)
    start_time = time.time()
    # Calculate LCM and add the result to the prompt
    numbers = []
    for element in st.session_state["lcm"]:
        numbers.append(element["denominator"])
    result = Function.LCM(numbers)
    lcm_prompt = '分母'+','.join(str(x) for x in numbers) + f"的最小公倍数是{result}，通分后的分母也应该是{result}，其他回答均错误！"
    if teacher_dialog == None or student_dialog == None:
        return None
    prompt = f'''以下是题目和教师与学生的对话，请你逐步思考，再判断学生的回答是否正确，**最后生成【正确】或【不正确】**
## 注意：
**{lcm_prompt}**
2. 请以尽量简短的话语来进行逐步思考，不要太过冗长
3. 请在结尾生成【正确】或【不正确】
4. **你不需要去解题，只要判断学生的回答对于老师当前的提问是否正确**

### 题目
{question}
### 教师
{teacher_dialog}
### 学生
{student_dialog}
'''
    model = "deepseek-r1:14b"
    response = get_llm_feedback_without_history(prompt, model)
    logger.info(f'''<<< LLM's checking whether student answer to guidance question is incorrect >>>
               【prompt】
                {prompt}
               【response】
                {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to}s  {len(response) / to} words/s")
    print("是否正確的判斷：" + response)
    return "不正确" in response[-10:]  # return whether the string "不正確" is present in the last part of response (True or False)


# This is the main tutor function to check student answer and offer tutoring if needed
def tutor(user_input, question, guidance_step, history):
    system = SYSTEM
    history.append({"role": "user", "content": user_input})
    header = ""
    # Check if a valid conversation history (i.e. with a minimum length of 2)
    if len(history) >= 2:
       # check if the student answer is incorrect
       is_incorrect_answer = check_student_incorrect_answer(history, question)   # Check if student answer is incorrect
       if is_incorrect_answer != None and is_incorrect_answer:     # if student answer is incorrect
          result = tutoring_for_student_error(question, history)   # offer tutoring
          result_display = sync_translate_tw(result)   # translate the result into traditional Chinese
          history.append({"role": "assistant", "content": result_display})
          return history, result

    start_time = time.time()
    header += f'''## 题目
{question}
## 当前引导步骤
{guidance_step}
## 学生输入\n
'''
    # response = guidance_step
    model = "qwen2.5"
    response = get_llm_feedback_with_history(user_input, history[:-1], header, model, system)
    history.append({"role": "assistant", "content": response})
    logger.info(f'''<<< LLM's response on step-by-step guidance >>>
               【prompt】
                {header + user_input}
               【response】
                {response}''')
    end_time = time.time()
    to = end_time - start_time
    logger.info(f"====TIME====  {to} s  {len(response) / to} words/s")
    st.session_state.messages_with_error = ''
    return history, response