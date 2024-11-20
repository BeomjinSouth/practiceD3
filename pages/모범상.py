import streamlit as st
from openai import OpenAI
import os

# Set up OpenAI configuration
MODEL = "gpt-4o"
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

# Initialize a list to store information about students
if 'student_entries' not in st.session_state:
    st.session_state['student_entries'] = []

# Function to add a new student entry
def add_student_entry():
    st.session_state['student_entries'].append({'award_name': '', 'student_name': '', 'student_quality': ''})

# Function to reset the session state
def reset_entries():
    st.session_state['student_entries'] = []
    st.session_state['recommendations'] = []

# UI Layout
st.title('학생 추천 상장 생성기')
st.write('교사로서 학생의 우수한 점을 기록하고 GPT-4o 모델을 활용해 추천 이유를 자동 생성하세요.')

# Loop through each student entry and create input fields
for idx, entry in enumerate(st.session_state['student_entries']):
    st.text_input(f"상의 이름 (학생 {idx + 1})", key=f"award_name_{idx}", value=entry['award_name'])
    st.text_input(f"학생 이름 (학생 {idx + 1})", key=f"student_name_{idx}", value=entry['student_name'])
    st.text_area(f"학생의 우수한 점 (학생 {idx + 1})", key=f"student_quality_{idx}", value=entry['student_quality'])
    st.write("---")

# Add Button to add new student entry
if st.button('+ 학생 추가'):
    add_student_entry()

# Generate Recommendations Button
if st.button('생성'):
    student_data = []
    for idx in range(len(st.session_state['student_entries'])):
        award_name = st.session_state[f"award_name_{idx}"]
        student_name = st.session_state[f"student_name_{idx}"]
        student_quality = st.session_state[f"student_quality_{idx}"]

        # Collect the data into a structured format
        student_data.append({
            'award_name': award_name,
            'student_name': student_name,
            'student_quality': student_quality
        })

    # Create a prompt for each student to get a recommendation
    recommendations = []
    for student in student_data:
        prompt = (
            f"You are a helpful assistant generating award recommendations. "
            f"Generate a reason why {student['student_name']} should receive the '{student['award_name']}' award. "
            f"The student's qualities are: {student['student_quality']}"
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        recommendation = response.choices[0].message.content
        recommendations.append({
            'student_name': student['student_name'],
            'award_name': student['award_name'],
            'recommendation': recommendation
        })

    # Store the recommendations in the session state for display
    st.session_state['recommendations'] = recommendations

# Display Recommendations
if 'recommendations' in st.session_state:
    st.subheader('추천 이유')
    for recommendation in st.session_state['recommendations']:
        st.write(f"**{recommendation['student_name']}** 학생의 '{recommendation['award_name']}' 상 추천 이유:")
        st.write(f"{recommendation['recommendation']}")
        st.write("---")

# Reset Button to clear all entries and recommendations
if st.button('초기화'):
    reset_entries()
