import streamlit as st
import PyPDF2
import io
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

st.title("설계안 도우미 챗봇 - 성호중 박범진")

# PDF 파일 업로드 부분 추가
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    # PDF 파일 읽기
    reader = PyPDF2.PdfFileReader(io.BytesIO(uploaded_file.getvalue()))
    text = ''
    for page in range(reader.getNumPages()):
        text += reader.getPage(page).extractText()

    # OpenAI GPT-4 모델을 사용하여 분석 요청
    response = client.Completion.create(
        model="gpt-4o",  # 모델을 GPT-4로 지정
        prompt=text,
        max_tokens=500
    )

    # 분석 결과 표시
    st.write("분석 결과:", response['choices'][0]['text'])
