import streamlit as st
from openai import OpenAI
import os

# OpenAI API 키 설정
api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 모델 이름 설정
MODEL = "gpt-4o-mini"

# 학생 정보 저장을 위한 리스트 초기화
if 'student_entries' not in st.session_state:
    st.session_state['student_entries'] = []

# 추천 이유 저장을 위한 리스트 초기화
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = []

# 새로운 학생 항목 추가 함수
def add_student_entry():
    st.session_state['student_entries'].append({'award_name': '', 'student_name': '', 'student_quality': ''})

# 입력 필드 초기화 함수
def reset_entries():
    st.session_state['student_entries'] = []
    st.session_state['recommendations'] = []

# UI 레이아웃 설정
st.title('학생 추천 상장 생성기')
st.write('학생의 우수한 점을 기록하고 GPT-4o-mini 모델을 활용해 추천 이유를 자동 생성하세요.')

# 각 학생 항목에 대한 입력 필드 생성
for idx, entry in enumerate(st.session_state['student_entries']):
    award_name = st.text_input(f"상의 이름 (학생 {idx + 1})", key=f"award_name_{idx}", value=entry['award_name'])
    student_name = st.text_input(f"학생 이름 (학생 {idx + 1})", key=f"student_name_{idx}", value=entry['student_name'])
    student_quality = st.text_area(f"학생의 우수한 점 (학생 {idx + 1})", key=f"student_quality_{idx}", value=entry['student_quality'])
    st.write("---")
    # 입력된 값을 세션 상태에 저장
    st.session_state['student_entries'][idx] = {
        'award_name': award_name,
        'student_name': student_name,
        'student_quality': student_quality
    }

# 학생 추가 버튼
if st.button('+ 학생 추가'):
    add_student_entry()

# 추천 이유 생성 버튼
if st.button('생성'):
    student_data = st.session_state['student_entries']
    recommendations = []

    for student in student_data:
        prompt = (
            f"당신은 도움이 되는 조수입니다. "
            f"{student['student_name']} 학생이 '{student['award_name']}' 상을 받아야 하는 이유를 생성해 주세요. "
            f"학생의 우수한 점은 다음과 같습니다: {student['student_quality']}"
        )

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "당신은 도움이 되는 조수입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            recommendation = response.choices[0].message.content.strip()
        except Exception as e:
            recommendation = f"추천 이유를 생성하는 중 오류 발생: {str(e)}"

        recommendations.append({
            'student_name': student['student_name'],
            'award_name': student['award_name'],
            'recommendation': recommendation
        })

    # 추천 이유를 세션 상태에 저장
    st.session_state['recommendations'] = recommendations

# 추천 이유 표시
if st.session_state['recommendations']:
    st.subheader('추천 이유')
    for recommendation in st.session_state['recommendations']:
        st.write(f"**{recommendation['student_name']}** 학생의 '{recommendation['award_name']}' 상 추천 이유:")
        st.write(f"{recommendation['recommendation']}")
        st.write("---")

# 초기화 버튼
if st.button('초기화'):
    reset_entries()
