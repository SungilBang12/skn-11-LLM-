import streamlit as st
import ollama
import random

# mbti 목록: 후에 랜덤으로 돌려 값을 주기 위해
mbti_types = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
              "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]

st.title("mbti 맞추기")
st.caption("A Streamlit chatbot powered by EEVE")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if 'ai_mbti' not in st.session_state:
    # 랜덤 돌리기
    st.session_state.ai_mbti = random.choice(mbti_types)
    # 시스템 메시지로 AI에게 mbti 주기
    system_message = f"너와 나는 mbti 맞추기 놀이를 할거야. 너는 {st.session_state.ai_mbti} 성격유형을 가진 AI로써 질문에 답할 때 {st.session_state.ai_mbti}의 특성을 반영해서 대답해야 해. 이건 역할놀이로써 너 자체의 성격 등을 설명하지 않는다는 것을 사용자도 알기 때문에 너가 이를 상기해 줄 필요는 없어. 이건 사용자의 mbti를 설명하는 것이 아닌, 너가 부여받은 {st.session_state.ai_mbti}로서 너의 성격을 묘사하는 거야. 직접적으로 너의 성격이 어떤 성향인지 이야기할 순 없어."
    st.session_state.messages = [
        {'role': 'system', 'content': system_message}, 
        {'role': 'assistant', 'content': '제 mbti는 무엇일까요? 10번 이내에 맞춰 보세요!'}
    ]

# 남은 기회와 게임 상태 초기화
if 'guess_count' not in st.session_state:
    st.session_state.guess_count = 0

if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# 대화 내역 표시 (시스템 메시지 제외)
for message in st.session_state.messages:
    if message["role"] != "system":  # 시스템 메시지는 표시하지 않음
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input('질문을 입력하세요: '):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 추측 횟수 증가
    st.session_state.guess_count += 1
    
    # MBTI 추측 확인
    user_guess = None
    if "mbti는" in prompt.lower() or "mbti 는" in prompt.lower():
        for mbti in mbti_types:
            if mbti in prompt.upper():
                user_guess = mbti
                break
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if user_guess:
            if user_guess == st.session_state.ai_mbti:
                response_text = f"정답입니다! 제 MBTI는 {st.session_state.ai_mbti}입니다. 축하합니다! {st.session_state.guess_count}번 만에 맞추셨네요."
                st.session_state.game_over = True
            else:
                if st.session_state.guess_count >= 10:
                    response_text = f"아쉽게도 기회를 모두 사용하셨습니다. 제 MBTI는 {st.session_state.ai_mbti}입니다."
                    st.session_state.game_over = True
                else:
                    response_text = f"{user_guess}는 아닙니다. 다시 생각해보세요! (남은 기회: {10 - st.session_state.guess_count}번)"
        else:
            # 일반 대화 응답
            if st.session_state.guess_count >= 10:
                response_text = f"기회를 모두 사용하셨습니다. 제 MBTI는 {st.session_state.ai_mbti}입니다."
                st.session_state.game_over = True
            else:
                # Ollama에 전달할 메시지 - 시스템 메시지 포함

                response = ollama.chat(
                model="EEVE-Korean-10.8B",
                messages=st.session_state.messages
                            )
                response_text = response['message']['content']
                for word in mbti_types:
                    if word in response_text:
                        response_text = response_text.replace(word, '****')

        
        message_placeholder.markdown(response_text)
    
    # 어시스턴트 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # # 게임이 끝났으면 새 게임 버튼 표시
    # if st.session_state.game_over:
    #     if st.button("새 게임 시작하기"):
    #         # 게임 초기화
    #         st.session_state.ai_mbti = random.choice(mbti_types)
    #         system_message = f"너는 {st.session_state.ai_mbti} 성격유형을 가진 AI야. 질문에 답할 때 {st.session_state.ai_mbti}의 특성을 반영해서 대답해. 하지만 직접적으로 자신의 MBTI를 언급하진 마."
    #         st.session_state.messages = [
    #             {'role': 'system', 'content': system_message}, 
    #             {'role': 'assistant', 'content': '제 mbti는 무엇일까요? 10번 이내에 맞춰 보세요!'}
    #         ]
    #         st.session_state.guess_count = 0
    #         st.session_state.game_over = False
    #         st.experimental_rerun()