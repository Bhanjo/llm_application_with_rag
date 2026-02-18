import streamlit as st
from dotenv import load_dotenv
from llm import getAIResponse

load_dotenv()

# page config
st.set_page_config(page_title="소득세 챗봇", page_icon=":money_with_wings:", layout="wide")
st.title("소득세 챗봇")
st.caption("소득세에 관련된 모든것을 대답해드립니다!")

# streamlit은 hotload 시 코드를 아예 다시 실행함. 즉, 이전 내용을 기억하지 못하기 때문에  session_state에 저장
if 'message_list' not in st.session_state:
    st.session_state['message_list'] = []

for message in st.session_state['message_list']:
    with st.chat_message(message['role']):
        st.write(message['content'])

if user_question := st.chat_input(placeholder="소득세 관련 질문을 입력하세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state['message_list'].append({"role": "user", "content": user_question})

    with st.spinner("답변을 생성하는 중입니다."):
        ai_response = getAIResponse(user_question)
        with st.chat_message('ai'):
            ai_message = st.write_stream(ai_response)
            st.session_state['message_list'].append({'role': 'ai', 'content': ai_message})

