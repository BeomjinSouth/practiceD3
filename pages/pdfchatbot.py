import streamlit as st
import pdfplumber
import io
from PIL import Image
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

st.title("설계안 도우미 챗봇 - 성호중 박범진")

# PDF 파일 업로드 부분 추가
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        text = ''
        for page in pdf.pages:
            # 텍스트 추출
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

            # 이미지 추출 및 간단한 설명 추가
            images = page.images
            if images:
                text += "페이지에 포함된 이미지 수: {}\n".format(len(images))

        # 전체 PDF 내용을 GPT-4 모델에 전달
        if text:
            prompt = "다음 문서에 대해 설명해주세요: \n\n" + text
            response = client.Completion.create(
                model="gpt-4o",
                prompt=prompt,
                max_tokens=1024
            )

            # 분석 결과 표시
            st.write("분석 결과:", response['choices'][0]['text'])
