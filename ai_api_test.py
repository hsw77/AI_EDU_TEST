import streamlit as st
import time
from openai import OpenAI
import json

# 페이지 설정
st.set_page_config(page_title="OpenAI Assistant Chatbot", page_icon="🤖")
st.title("OpenAI Assistant Chatbot 💬")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "openai_client" not in st.session_state:
    st.session_state.openai_client = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# API 키 입력 섹션
with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        st.session_state.openai_client = OpenAI(api_key=api_key)
        
        # 스레드 생성 (첫 실행시)
        if not st.session_state.thread_id:
            thread = st.session_state.openai_client.beta.threads.create()
            st.session_state.thread_id = thread.id

# Assistant ID 설정
ASSISTANT_ID = "asst_4OJeo5O3pUziKKm923PPbTxV"

def get_assistant_response(client, thread_id, user_message):
    # 메시지 생성
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )
    
    # 실행 생성
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )
    
    # 실행 완료 대기
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(0.5)
    
    # 메시지 검색
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    # 최신 응답 반환
    return messages.data[0].content[0].text.value

# 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    if not api_key:
        st.error("OpenAI API 키를 입력해주세요!")
    else:
        # 사용자 메시지 표시
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 로딩 표시
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("생각하는 중...")
            
            try:
                # Assistant 응답 받기
                response = get_assistant_response(
                    st.session_state.openai_client,
                    st.session_state.thread_id,
                    prompt
                )
                
                # 응답 표시
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                message_placeholder.empty()