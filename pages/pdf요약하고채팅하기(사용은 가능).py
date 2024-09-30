import streamlit as st
import pdfplumber
import io
from openai import OpenAI

# OpenAI 클라이언트 생성 및 API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

# Streamlit 앱 제목 및 안내 문구
st.title("설계안 도우미 챗봇 - 성호중 박범진")
st.write("PDF 를 업로드하고 질문을 작성한 뒤 엔터를 눌러주세요. 오른쪽 위 'Running'이 끝나면 답변이 출력됩니다.")

# 세션 상태 초기화
if 'knowledge_base' not in st.session_state:
    st.session_state['knowledge_base'] = ""

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# PDF 파일 업로드
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

        st.session_state['knowledge_base'] = text
        st.write("PDF에서 추출된 내용이 지식 베이스로 저장되었습니다.")

# 대화 초기화 버튼
if st.button('대화 초기화'):
    st.session_state['messages'] = []
    st.write("대화가 초기화되었습니다.")

# 사용자 질문 입력
user_query = st.text_input("질문을 입력하세요:")

# 사용자 질문 처리
if user_query:
    # 지식 베이스가 존재하는지 확인
    if st.session_state['knowledge_base']:
        # 메시지 초기화 및 시스템 프롬프트 추가
        if not st.session_state['messages']:
            st.session_state['messages'].append(
                {"role": "system", "content": f"다음 문서 내용을 바탕으로 질문에 답해주세요:\n{st.session_state['knowledge_base']}"}
            )
        # 사용자 메시지 추가
        st.session_state['messages'].append({"role": "user", "content": user_query})

        # 이전 대화 내용 표시
        for message in st.session_state['messages']:
            if message['role'] == 'user':
                st.write(f"**사용자:** {message['content']}")
            elif message['role'] == 'assistant':
                st.write(f"**GPT의 답변:** {message['content']}")

        # GPT 응답 생성 중 스피너 표시
        with st.spinner('GPT가 응답을 생성 중입니다...'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",  # 또는 "gpt-4"를 사용하려면 해당 권한 필요
                    messages=st.session_state['messages'],
                    temperature=0.7,
                )
                # response에서 content를 가져올 때 객체로 접근
                answer = response.choices[0].message.content

                # 어시스턴트 응답 추가
                st.session_state['messages'].append({"role": "assistant", "content": answer})

                # 어시스턴트 응답 표시
                st.write(f"**GPT의 답변:** {answer}")

                # 질문 입력 필드 초기화: 여기서 session_state를 수정하는 대신 빈 값으로 초기화
                st.text_input("질문을 입력하세요:", value='', key="user_query", help="새로운 질문을 입력하세요.")
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")

        # 메시지 구분선 추가
        st.markdown("---")
    else:
        st.warning("먼저 PDF 파일을 업로드하여 지식 베이스를 생성해주세요.")
else:
    # 이전 대화 내용 표시
    if st.session_state['messages']:
        for message in st.session_state['messages']:
            if message['role'] == 'user':
                st.write(f"**사용자:** {message['content']}")
            elif message['role'] == 'assistant':
                st.write(f"**GPT의 답변:** {message['content']}")
