import streamlit as st
from openai import OpenAI
import os

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

# 모델 이름 설정
MODEL = "gpt-4o-mini"

# 세션 상태 초기화
if 'student_entries' not in st.session_state:
    st.session_state['student_entries'] = []
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = []

# 학생 항목 추가 함수
def add_student_entry():
    st.session_state['student_entries'].append({'award_name': '', 'student_name': '', 'student_quality': ''})

# 세션 상태 초기화 함수
def reset_entries():
    st.session_state['student_entries'] = []
    st.session_state['recommendations'] = []

# UI 레이아웃
st.title('학생 추천 상장 생성기')
st.write('학생의 우수한 점을 기록하고 GPT-4o-mini 모델을 활용해 추천 이유를 자동 생성하세요.')

# 각 학생 항목에 대한 입력 필드 생성
for idx, entry in enumerate(st.session_state['student_entries']):
    entry['award_name'] = st.text_input(f"상의 이름 (학생 {idx + 1})", value=entry['award_name'], key=f"award_name_{idx}")
    entry['student_name'] = st.text_input(f"학생 이름 (학생 {idx + 1})", value=entry['student_name'], key=f"student_name_{idx}")
    entry['student_quality'] = st.text_area(f"학생의 우수한 점 (학생 {idx + 1})", value=entry['student_quality'], key=f"student_quality_{idx}")
    st.write("---")

# 학생 추가 버튼
if st.button('+ 학생 추가'):
    add_student_entry()

# 생성 버튼
if st.button('생성'):
    recommendations = []
    for entry in st.session_state['student_entries']:
        prompt = (
            f"'{entry['award_name']}' 상을 받을 학생인 {entry['student_name']}의 우수한 점은 다음과 같습니다: {entry['student_quality']}. "
            f"이러한 점을 바탕으로 추천 이유를 작성해 주세요."
        )

        try:
            response = client.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 조수입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            recommendation = response.choices[0].message['content'].strip()
        except Exception as e:
            recommendation = f"오류 발생: {str(e)}"

        recommendations.append({
            'student_name': entry['student_name'],
            'award_name': entry['award_name'],
            'recommendation': recommendation
        })

    st.session_state['recommendations'] = recommendations

# 추천 이유 표시
if st.session_state['recommendations']:
    st.subheader('추천 이유')
    for rec in st.session_state['recommendations']:
        st.write(f"**{rec['student_name']}** 학생의 '{rec['award_name']}' 상 추천 이유:")
        st.write(f"{rec['recommendation']}")
        st.write("---")

# 초기화 버튼
if st.button('초기화'):
    reset_entries()
