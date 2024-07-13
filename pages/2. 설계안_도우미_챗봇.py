import streamlit as st
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

st.title("설계안 도우미 챗봇")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

system_message = '''
# 체크리스트 검토

## 역할
당신은 교사가 디지털 플랫폼(AI 디지털 교과서)를 활용한 수업 설계안을 작성하려고 할 때, 적절히 도움과 조언을 제공해야 합니다
수업의 각 단계에 대해 조언을 해줄 때, 관련된 다양한 사례를 함께 제공합니다
질문에 대해 답안을 먼저 제시하기보다, 추가적인 정보를 요구하여 디테일하게 대답합니다

## 규칙
1. **제공된 정보를 토대로 수업 설계안 작성을 위한 도움을 제공함**:
2. **곧바로 답변하기에 너무 포괄적인 질문인 경우 추가적인 정보를 요청한다**
3. AI 디지털 교과서의 기능들을 시의적절하게 활용할 수 있는 수업이 될 수 있게 조언한다

## 참고사항
1. 디지털 기기를 활용한 수업을 만든다는 것을 고려할 것
2. 수업시간은 50분
3. **수업에서 디지털 플랫폼을 활용할 때 변화하는 수업 환경을 고려할 것**
4. **디지털 플랫폼(AI디지털교과서)의 기능을 다양한 상황에 적용할 수 있게 조언할 것**

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
12. 팀빌딩 : 학생의 성취도에 따라 적절한 모둠을 구성
   
### 어투
- 예의를 갖추어 대답할 것 
'''
# 시스템 메시지 초기화
if "design_messages" not in st.session_state:
    st.session_state.design_messages = []

if len(st.session_state.design_messages) == 0:
    st.session_state.design_messages = [{"role": "system", "content": system_message}]

for idx, message in enumerate(st.session_state.design_messages):
    if idx > 0:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("안녕하세요?"):
    st.session_state.design_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
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
