import streamlit as st
import pdfplumber
import io
from openai import OpenAI

# Streamlit 세션 상태 초기화
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = ""

client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

st.title("설계안 도우미 챗봇 - 성호중 박범진")

# PDF 파일 업로드
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

        st.session_state.knowledge_base = text
        st.write("PDF에서 추출된 내용이 지식 베이스로 저장되었습니다.")
# 사용자 질문 입력 및 처리
user_query = st.text_input("질문을 입력하세요:")
if user_query:
    messages = [
        {"role": "system", "content": f"다음 문서 내용을 바탕으로 질문에 답해주세요:\n{st.session_state.knowledge_base}"},
        {"role": "user", "content": user_query},
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,  # 스트리밍 활성화
        )
        placeholder = st.empty()
        full_reply_content = ''
        for chunk in response:
            chunk_message = chunk.choices[0].delta.get('content', '')
            full_reply_content += chunk_message
            placeholder.write("GPT-4의 답변: " + full_reply_content)
    except Exception as e:
        st.error(f"에러가 발생했습니다: {e}")
