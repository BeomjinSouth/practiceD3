import streamlit as st
from openai import OpenAI

# 페이지 제목 설정
st.title("체크리스트 도우미 챗봇")

# OpenAI API 키 설정
api_key = st.secrets["OPENAI"]["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 챗봇 설정 메시지
system_message = '''
# 체크리스트 검토

## 역할
당신은 교사가 수업 설계안에 대한 체크리스트를 작성할 때, 적절히 도움과 조언을 제공해야 합니다.
단순히 체크리스트의 예시만 제시하기보다, 어떠한 부분에서 그런 체크리스트가 요구되는지 같이 이야기합니다.
또한 추가적인 정보가 필요하다면 답안을 제시하기 전에 필요한 정보에 대해서 먼저 질문합니다

## 규칙
1. **제공된 정보를 토대로 수업 설계안을 체크하기 위한 체크리스트를 작성함**:
3. **곧바로 답변하기에 너무 포괄적인 질문인 경우 추가적인 정보를 요청**
2. **체크리스트 작성 방식**:
    - 각각의 체크리스트는 한 줄로 작성.
    - 체크리스트는 하나만 제시하지 않고, 2개 이상, 3개 이하로 제시할 것

## 수업 설계안에 활용할 수 있는 디지털 플랫폼(AI디지털교과서)의 기능
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
12. 팀빌딩 : 학생의 성취도에 따라 적절한 모둠을 구
   
## 어투
- 예의를 갖추어 대답할 것 
'''

# 시스템 메시지 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_message}]

# 챗 메시지 출력
for idx, message in enumerate(st.session_state.messages):
    if idx > 0:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI 모델 호출
    with st.chat_message("assistant"):
        response = client.chat_completions.create(
            model="gpt-4o",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=False,
        )
        for chunk in response:
            content = chunk["choices"][0].get("delta", {}).get("content", "")
            if content:
                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})
