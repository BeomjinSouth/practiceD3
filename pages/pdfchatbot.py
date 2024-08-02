import streamlit as st
import pdfplumber
import io
from PIL import Image

st.title("PDF 이미지 및 텍스트 추출기")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        for page in pdf.pages:
            # 텍스트 추출
            text = page.extract_text()
            st.write("페이지의 텍스트:", text)

            # 이미지 추출
            im = page.images
            for image in im:
                # 이미지 객체를 생성
                img_bytes = page.extract_image(image['object_id'])['image']
                # PIL 이미지 객체로 변환
                img = Image.open(io.BytesIO(img_bytes))
                # Streamlit에서 이미지 표시
                st.image(img, caption="페이지의 이미지")
