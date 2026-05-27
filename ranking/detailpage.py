from numpy import record
import streamlit as st
from services.components import draw_character_card
from services.utils import load_css

def detail_page_display():
    
    record = None
    # ==========================================
    # 💡 2. 꼬리표가 없다면? 세션 가방을 확인합니다! (랭킹 페이지에서 버튼 누르고 온 사람)
    # ==========================================
    if record is None:
        record = st.session_state.get("selected_record")

    # ==========================================
    # 💡 3. 둘 다 없으면? 그때서야 진짜 쫓아냅니다. (주소창에 이상한 거 치고 온 사람)
    # ==========================================
    if record is None:
        st.warning("선택된 기록이 없거나 잘못된 주소입니다.")
        if st.button("⬅️ 랭킹 게시판으로 돌아가기"):
            st.query_params.clear()
            st.switch_page("pages/rank.py")  # 랭킹 페이지로 돌아가기
        st.stop()

    # ==========================================
    # 💡 상세 화면이 켜질 때만 발동하는 전용 CSS! 
    # (목록으로 돌아가면 자동으로 사라져서 다른 페이지는 안전합니다)
    # ==========================================
    load_css('ranking/rankingdetailpage.css')
    # ==========================================
    prev_page = st.session_state.get("previous_page", "pages/rank.py")  # 이전 페이지 정보가 없으면 랭킹 페이지로 기본 설정

    if st.button("⬅️ 이전 페이지로 돌아가기"):
        st.query_params.clear()  # URL 꼬리표 초기화
        st.switch_page(prev_page)  # 랭킹 페이지로 돌아가기

    base_url= "https://r1999rr.streamlit.app"
    current_deck_code = record.get("deck_code", "")
    
    if current_deck_code:
        deck_url = f"{base_url}/?deck={current_deck_code}"

        # 💡 긴 URL을 완전히 숨기고 커스텀 버튼 디자인과 자바스크립트 동작을 묶어줍니다.
        custom_copy_button = f"""
        <style>
        .copy-btn {{
            width: 100%;
            background-color: #FF4B4B; /* 스트림릿 고유의 예쁜 레드 포인트 컬러 */
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 15px;
            font-weight: bold;
            border-radius: 8px; /* 둥근 모서리 */
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .copy-btn:hover {{
            background-color: #FF3333; /* 마우스 올렸을 때 살짝 진해짐 */
        }}
        </style>
        
        <button class="copy-btn" id="copy-btn" onclick="copyURL()">
            🔗 덱 코드 공유 링크 복사하기
        </button>

        <script>
        function copyURL() {{
            // 숨겨진 deck_url을 클립보드에 복사합니다.
            navigator.clipboard.writeText('{deck_url}').then(function() {{
                var btn = document.getElementById('copy-btn');
                
                // 💡 [클릭 시 애니메이션] 텍스트가 바뀌고 초록색으로 변합니다!
                btn.innerText = '✅ 링크가 복사되었습니다!';
                btn.style.backgroundColor = '#00CC66'; 
                
                // 2초 뒤에 원래 버튼 상태로 조용히 돌아갑니다.
                setTimeout(function() {{
                    btn.innerText = '🔗 덱 코드 공유 링크 복사하기';
                    btn.style.backgroundColor = '#FF4B4B';
                }}, 2000);
            }});
        }}
        </script>
        """
        
        # iframe(웹 페이지 속의 웹 페이지) 형태로 렌더링하며 높이를 기본 버튼과 똑같이 45px로 고정합니다.
        st.iframe(custom_copy_button, height=50)
        
    st.write("---")
    
    # 제목에 어떤 보스의 기록인지 표시해 줍니다.
    st.title(f"🏆 {record['nickname']}님의 [{record['boss_name']}] 공략")
    st.subheader(f"기록: {record['score']:,} 점")
    st.write("---")
    
    # ==========================================
    # 💡 [화면 B 수정] 다시 1줄 4칸으로 되돌리기
    # ==========================================
    st.markdown("### 👥 사용 덱 및 형상")
        
    draw_character_card(record) # 이 함수는 이제 record에서 바로 캐릭터/의지/형상/공명 정보를 꺼내서 그려줍니다!
        
    st.write("") 
    st.markdown(f"**💬 유저 코멘트:** {record['comment']}")
    st.write("---")
    
    # ==========================================
    # 💡 수정된 부분: DB에서 개별 사진을 불러옵니다!
    # ==========================================
    st.markdown("### 📸 인증 스크린샷")
    if record.get("proof_url"):
        st.image(record["proof_url"], width= 'stretch')
    else:
        st.info("등록된 스크린샷이 없습니다.")
    st.write("---")
    # ==========================================
    
    # 3. 플레이 영상 (세로 배치 3단)
    st.markdown("### 🎬 플레이 영상")
    if record["video_url"]: # 비디오 링크가 있으면 플레이어를 띄움
        # 스트림릿은 유튜브 링크나 mp4 링크를 넣으면 알아서 플레이어를 만들어 줍니다!
        st.video(record["video_url"])
    else:
        st.info("등록된 영상이 없습니다.")

