import streamlit as st
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

def request_chat_completion(
    prompt,
    system_role="""당신은 교수학습 설계에 능숙한 베테랑 교사입니다. 언급된 내용을 참고하여 해당 교과의 수업 설계안을 작성합니다. 수업 설계안을 작성할 때에는 도입, 전개, 마무리로 구분하여 작성하세요.
""",
    model="gpt-4o",
    stream=False
):
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream
    )
    return response

st.set_page_config(
    page_title="GPT API를 활용한 챗봇 - 성호중 박범진",
    page_icon="🎇"
)

st.title("GPT-4o를 활용한 설계안 만들어보기")
st.subheader("AI를 활용하여 설계안을 만들어봅시다")

if "form_data" not in st.session_state:
    st.session_state["form_data"] = {
        "subjects": "",
        "units": "",
        "topics": "",
        "keyword_1": "",
        "keyword_2": "",
        "keyword_3": "",
        "details": "",
        "must_include": "",
        "response": ""
    }

with st.form("form"):
    st.text("과목, 단원, 수업주제를 입력해주세요")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.form_data["subjects"] = st.text_input("과목", st.session_state.form_data["subjects"])
    with col2:
        st.session_state.form_data["units"] = st.text_input("단원", st.session_state.form_data["units"])
    with col3:
        st.session_state.form_data["topics"] = st.text_input("수업주제", st.session_state.form_data["topics"])
  
    st.text("수업에 대한 상세한 설명을 작성해주세요")
    st.session_state.form_data["details"] = st.text_area("수업 상세 설명", st.session_state.form_data["details"])
    
    st.text("수업에 꼭 넣고 싶은 것을 작성해주세요")
    st.session_state.form_data["must_include"] = st.text_area("꼭 넣고 싶은 것들", st.session_state.form_data["must_include"])
      
    submit = st.form_submit_button("Submit")

    if submit:
        with st.spinner("설계안을 생성 중입니다!"):
            prompt = f"수업시간은 45분이야. 과목: {st.session_state.form_data['subjects']}\n단원명: {st.session_state.form_data['units']}\n수업주제: {st.session_state.form_data['topics']}\n포함하고 싶은 AI 디지털 교과서 기능: {st.session_state.form_data['keyword_1']}, {st.session_state.form_data['keyword_2']}, {st.session_state.form_data['keyword_3']}\n수업 상세 설명: {st.session_state.form_data['details']}\n꼭 넣고 싶은 것들: {st.session_state.form_data['must_include']}"
            response = request_chat_completion(
                prompt=prompt,
                stream=False
            )
            st.session_state.form_data["response"] = response.choices[0].message.content

if st.session_state.form_data["response"]:
    st.success("제출 완료!")
    st.write(st.session_state.form_data["response"])
