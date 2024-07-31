import streamlit as st
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

def request_chat_completion(
    prompt,
    system_role="당신은 교수학습 설계에 능숙한 베테랑 교사입니다. 언급된 AI 디지털교과서의 기능들을 반영하여 해당 교과의 수업 설계안을 작성합니다. 수업 설계안을 작성할 때에는 도입, 전개, 마무리로 구분하여 작성하세요. 
## 활용할 수 있는 디지털 플랫폼(AI디지털교과서)의 기능
1. 학습 진단(학습 전) : 학습 이해도와 학습 진행 상황 등을 AI를 통해 진단
2. 학습 진단(학습 후) : 학습 후 학습 목표 달성 여부를 확인
3. 맞춤형 콘텐츠 추천 : 학습자의 흥미, 수준, 학습 상황을 고려한 콘텐츠 추천
4. 오답노트 : 학습 과정에서 오답 노트가 누적되어 지난 시간에 틀린 내용을 다시 복습 가능
5. 대시보드 : 학생(혹은 학급 전체)의 학습 상황(참여도, 성취도 등)을 한 눈에 파악 가능
6. AI 튜터(학습전략제안) : 학생의 강약점을 식별하고 학습 수준에 맞게 학습 전략 제안
7. AI 보조교사 : AI를 통해 교사의 수업 설계, 피드백, 평가, 학생 모니터링 등을 지원
8. AI 튜터(추가 학습 자료 제공) : 학생의 학습 데이터를 분석하고 수준에 맞는 보충 과제를 AI가 제공
9. AI 튜터(질의응답) : AI에게 궁금한 내용을 질문하면 AI가 대답
10. 모니터링 : 학생의 학습 과정을 실시간으로 확인하고 피드백 제공
11. 콘텐츠 재구성 : 교사가 디지털 교과서의 콘텐츠를 변경, 재구성
12. 팀빌딩 : 학생의 성취도에 따라 적절한 모둠을 구성",
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

st.title("GPT-4를 활용한 설계안 만들어보기")
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
    
    st.text("포함하고 싶은 AIDT의 기능을 최대 3개까지 입력해주세요")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.session_state.form_data["keyword_1"] = st.text_input("AIDT 기능 1", st.session_state.form_data["keyword_1"])
    with col5:
        st.session_state.form_data["keyword_2"] = st.text_input("AIDT 기능 2", st.session_state.form_data["keyword_2"])
    with col6:
        st.session_state.form_data["keyword_3"] = st.text_input("AIDT 기능 3", st.session_state.form_data["keyword_3"])
  
    st.text("수업에 대한 상세한 설명을 작성해주세요")
    st.session_state.form_data["details"] = st.text_area("수업 상세 설명", st.session_state.form_data["details"])
    
    st.text("수업에 꼭 넣고 싶은 것을 작성해주세요")
    st.session_state.form_data["must_include"] = st.text_area("꼭 넣고 싶은 것들", st.session_state.form_data["must_include"])
      
    submit = st.form_submit_button("Submit")

    if submit:
        with st.spinner("설계안을 생성 중입니다!"):
            prompt = f"수업시간은 50분이야. 과목: {st.session_state.form_data['subjects']}\n단원명: {st.session_state.form_data['units']}\n수업주제: {st.session_state.form_data['topics']}\n포함하고 싶은 AI 디지털 교과서 기능: {st.session_state.form_data['keyword_1']}, {st.session_state.form_data['keyword_2']}, {st.session_state.form_data['keyword_3']}\n수업 상세 설명: {st.session_state.form_data['details']}\n꼭 넣고 싶은 것들: {st.session_state.form_data['must_include']}"
            response = request_chat_completion(
                prompt=prompt,
                stream=False
            )
            st.session_state.form_data["response"] = response.choices[0].message.content

if st.session_state.form_data["response"]:
    st.success("제출 완료!")
    st.write(st.session_state.form_data["response"])
