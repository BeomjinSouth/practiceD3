import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 계정 데이터를 로드하는 함수
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 계정 데이터를 저장하는 함수
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)

# 학습 데이터를 로드하는 함수
def load_learning_data():
    try:
        with open("learning_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 학습 데이터를 저장하는 함수
def save_learning_data(learning_data):
    with open("learning_data.json", "w") as file:
        json.dump(learning_data, file)

# 이메일을 전송하는 함수
def send_email(to_email, subject, body):
    # SMTP 서버 설정 (Gmail을 사용)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@gmail.com"  # 실제 Gmail 주소로 변경하세요.
    smtp_password = st.secrets["EMAIL_PASSWORD"]  # 비밀번호는 secrets에서 불러옵니다.

    # 이메일 메시지 작성
    msg = MIMEMultipart()
    msg['From'] = smtp_user  # 보내는 사람의 이메일 주소
    msg['To'] = to_email  # 받는 사람의 이메일 주소
    msg['Subject'] = subject  # 이메일 제목

    # 이메일 본문 작성
    body = MIMEText(body, 'plain')
    msg.attach(body)

    # SMTP 서버에 연결하여 이메일을 전송합니다.
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # TLS (Transport Layer Security) 시작
        server.login(smtp_user, smtp_password)  # SMTP 서버에 로그인
        server.sendmail(smtp_user, to_email, msg.as_string())  # 이메일 전송

# 대분류와 소분류에 따른 주제 목록
topics = {
    "영어": {
        "문법": ["수동태", "현재완료", "관계대명사"],
        "독해": ["지문 해석", "어휘 문제"],
        "어휘": ["고급 어휘", "동의어"]
    },
    "수학": {
        "대수": ["방정식", "함수"],
        "기하": ["삼각형", "원"]
    },
    "과학": {
        "물리": ["역학", "전기"],
        "화학": ["화학 반응", "주기율표"]
    }
}

# 메인 애플리케이션 함수
def app():
    st.title("학습 도우미 시스템")

    # 로그인 상태를 확인하기 위한 세션 상태 변수 초기화
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # 사용자가 로그인한 상태인지 확인하여 다른 화면을 표시합니다.
    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")

        # 세션 상태 초기화 - 처음 페이지 로드 시 필요
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o-mini"  # 사용할 OpenAI 모델 설정
        if "design_messages" not in st.session_state:
            st.session_state.design_messages = []  # 메시지 히스토리 초기화
        if "question_generated" not in st.session_state:
            st.session_state["question_generated"] = False  # 문제 생성 상태 초기화

        # 대분류 선택
        main_category = st.selectbox("대분류를 선택하세요", list(topics.keys()))
        
        # 소분류 선택
        sub_category = st.selectbox("소분류를 선택하세요", list(topics[main_category].keys()))
        
        # 주제 선택
        topic = st.selectbox("주제를 선택하세요", topics[main_category][sub_category])

        # 문항 개수 및 난이도 선택
        num_questions = st.number_input('문항 개수를 선택하세요', min_value=1, max_value=10, value=3)
        difficulty = st.selectbox('난이도를 선택하세요', ['쉬움', '보통', '어려움'])
        question_type = st.selectbox('문항 유형을 선택하세요', ['논술형', '객관식'])

        # GPT API를 사용해 문항을 생성 요청
        if st.button('생성하기'):
            # 이전 대화 초기화
            st.session_state.design_messages = []
            
            prompt = f"{main_category} - {sub_category}: '{topic}' 주제의 {num_questions}개의 문항을 생성해줘. 난이도는 {difficulty}이고, 문항 유형은 {question_type}이다."
            st.session_state.design_messages.append({"role": "user", "content": prompt})

            # GPT 응답을 생성하여 출력합니다.
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.design_messages
                    ],
                    stream=True,
                )

                # Streamlit의 최신 기능을 사용하여 스트리밍된 응답을 출력합니다.
                response = st.write_stream(stream)
                
                # 중복 추가 방지
                if not any(msg["content"] == response for msg in st.session_state.design_messages):
                    st.session_state.design_messages.append({"role": "assistant", "content": response})

                st.session_state["question_generated"] = True  # 문제 생성 상태 갱신

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

        # 학생의 질문과 GPT의 응답을 항상 입력칸 위에 표시
        if st.session_state.get("question_generated"):
            for message in st.session_state.design_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # 학생의 답변 또는 질문을 위한 텍스트 박스와 버튼 표시
            student_input = st.text_area('여기에 질문이나 답변을 입력하세요', key="student_input")
            
            col1, col2, col3 = st.columns([3, 1, 1])

            with col2:
                if st.button('질문하기'):
                    st.session_state.design_messages.append({"role": "user", "content": student_input})

                    # 사용자에게 입력한 질문을 표시합니다.
                    with st.chat_message("user"):
                        st.markdown(student_input)

                    # GPT와의 대화를 이어갑니다.
                    try:
                        stream = client.chat.completions.create(
                            model=st.session_state["openai_model"],
                            messages=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.design_messages
                            ],
                            stream=True,
                        )

                        response = st.write_stream(stream)
                        st.session_state.design_messages.append({"role": "assistant", "content": response})

                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

            with col3:
                if st.button('얘기하기'):
                    st.session_state.design_messages.append({"role": "user", "content": student_input})

                    # 사용자에게 입력한 요청을 표시합니다.
                    with st.chat_message("user"):
                        st.markdown(student_input)

                    # GPT와의 대화를 이어갑니다.
                    try:
                        stream = client.chat.completions.create(
                            model=st.session_state["openai_model"],
                            messages=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.design_messages
                            ],
                            stream=True,
                        )

                        response = st.write_stream(stream)
                        st.session_state.design_messages.append({"role": "assistant", "content": response})

                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

                if st.button('평가 요청'):
                    # GPT에게 학생의 답변을 평가하도록 요청합니다.
                    st.session_state.design_messages.append({"role": "user", "content": student_input})

                    with st.chat_message("assistant"):
                        evaluation_prompt = f"학생의 답변을 평가해주세요: {student_input}"
                        st.session_state.design_messages.append({"role": "user", "content": evaluation_prompt})

                        try:
                            stream = client.chat.completions.create(
                                model=st.session_state["openai_model"],
                                messages=[
                                    {"role": m["role"], "content": m["content"]}
                                    for m in st.session_state.design_messages
                                ],
                                stream=True,
                            )

                            response = st.write_stream(stream)
                            st.session_state.design_messages.append({"role": "assistant", "content": response})

                        except Exception as e:
                            st.error(f"오류가 발생했습니다: {e}")

                    # 선생님에게 전체 대화 내역을 이메일로 전송
                    teacher_email = "teacher_email@gmail.com"  # 선생님의 이메일로 변경하세요.
                    all_messages = "\n\n".join([f"{m['role']}: {m['content']}"] for m in st.session_state.design_messages)
                    send_email(teacher_email, "학생과의 대화 내역", all_messages)

                    # 학생에게 평가 결과를 이메일로 전송
                    try:
                        send_email(st.session_state['email'], "평가 결과", response)
                        st.success("평가가 완료되었으며 학생의 이메일로 전송되었습니다.")
                    except smtplib.SMTPAuthenticationError:
                        st.error("이메일 인증에 실패했습니다. SMTP 설정을 확인해주세요.")

                    # 학습 데이터를 저장
                    learning_data = load_learning_data()
                    email = st.session_state['email']
                    if email not in learning_data:
                        learning_data[email] = []

                    learning_data[email].append({
                        "timestamp": str(datetime.now()),
                        "subject": main_category,
                        "sub_topic": sub_category,
                        "specific_topic": topic,
                        "questions": response,
                        "responses": student_input,
                        "evaluation": response
                    })
                    save_learning_data(learning_data)

                    # 상태를 초기화하여 다음 입력을 받을 준비를 합니다.
                    st.session_state['response_complete'] = False
                    st.session_state["question_generated"] = False

    else:
        # 로그인하지 않은 상태에서 로그인 및 계정 생성 화면을 표시합니다.
        st.header("로그인 또는 계정 생성")

        email = st.text_input("이메일을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")

        accounts = load_accounts()

        # 사용자가 입력한 이메일과 비밀번호를 확인하여 로그인 처리합니다.
        if st.button("로그인"):
            if email in accounts and accounts[email] == password:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email  # 로그인한 사용자의 이메일을 세션 상태에 저장
                st.experimental_set_query_params(logged_in="true")
            else:
                st.error("이메일 또는 비밀번호가 일치하지 않습니다.")

        # 계정을 새로 생성합니다.
        if st.button("계정 등록"):
            if email in accounts:
                st.error("이미 존재하는 이메일입니다.")
            else:
                accounts[email] = password
                save_accounts(accounts)
                st.success("계정이 성공적으로 등록되었습니다.")

if __name__ == "__main__":
    app()
