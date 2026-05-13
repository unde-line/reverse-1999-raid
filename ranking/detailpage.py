from numpy import record
import streamlit as st
from services.components import draw_character_card
from services.utils import load_css
import services.DB

def detail_page_display():
    
    record = None
    
    # ==========================================
    # 💡 1. URL 꼬리표(Query Params)가 있는지 먼저 확인합니다! (친구한테 링크 받고 온 사람)
    # ==========================================
    url_user = st.query_params.get("user")
    url_boss = st.query_params.get("boss")
    
    if url_user and url_boss:
        # DB에서 해당 보스의 기록들을 싹 가져옵니다.
        board_data = services.DB.load_board_data()
        boss_records = board_data.get(url_boss, [])
        
        # 가져온 기록 중에서 닉네임이 일치하는 사람을 찾습니다!
        for r in boss_records:
            if r["nickname"] == url_user:
                record = r
                record["boss_name"] = url_boss
                break

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

