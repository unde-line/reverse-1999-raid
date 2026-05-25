import streamlit as st
from services.DB import upload_storage_image, insert_new_record, code_to_deck
from services.utils import to_analyze_recommended_decks, generate_deck_code
from services.config import CURRENT_SEASON_BOSSES
from editrecord.editUI import draw_character_slots, draw_preset_buttons
import random
import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@st.dialog("✨ 새로운 레이드 기록 등록", width="large")
def show_register_popup():
    

    st.write("리버스: 1999 레이드 기록을 등록해 주세요. (관리자 승인 후 반영됩니다)")
    if "random_nickname" not in st.session_state:
        st.session_state["random_nickname"] = f"버틴-{random.randint(1000, 9999)}"
    with st.expander("🔗 덱 코드로 파티 정보 자동 기입하기", expanded=False):
        st.caption("공유받은 8자리 코드나 전체 링크를 입력하면 캐릭터 세팅이 자동으로 채워집니다.")
        
        # 1. 입력창과 버튼을 나란히 배치
        code_col1, code_col2 = st.columns([7.5, 2.5], vertical_alignment="bottom")
        
        with code_col1:
            input_deck_val = st.text_input(
                "덱 코드 또는 링크 붙여넣기", 
                placeholder="예: D5822CD4 또는 https://...",
                key="deck_code_input_field"
            ).strip()
            
        with code_col2:
            if st.button("🚀 불러오기", width='stretch', type="primary"):
                code_to_deck(input_deck_val)
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # 약간의 여백

    st.divider()

    # ========================================================
    # 💡 1. 보스 선택창을 무조건 '가장 위로' 끌어올립니다!
    # ========================================================
    st.markdown("### 👹 보스 및 기본 정보")
    col1, col2 = st.columns(2)
    with col1:
        # 💡 이제 코드가 위에서부터 읽히면서 'selected_boss' 변수에 
        # 유저가 방금 고른 보스 이름이 정확하게 실시간으로 담깁니다.
        selected_boss = st.selectbox("보스 선택", CURRENT_SEASON_BOSSES, key="reg_boss")
    with col2:
        score = st.number_input("🏆 점수", min_value=0, step=10000, format="%d", key="reg_score")

    # ========================================================
    # 💡 2. 보스를 고른 상태에서 그 보스의 프리셋을 가져오도록 버튼을 아래에 배치합니다!
    # ========================================================
    draw_preset_buttons(selected_boss)
    st.divider()
        
    col3, col4 = st.columns(2)
    with col3:
        nickname = st.text_input("👤 닉네임 (최대 10자)", max_chars=10, key="reg_nickname", placeholder=st.session_state["random_nickname"])
    with col4:
        password = st.text_input("🔒 글 비밀번호 (수정/삭제용)", type="password", max_chars=20, key="reg_password")

    st.divider()
    st.markdown("### 👥 파티 구성")
    st.caption("💡 팁: 캐릭터와 의지 칸을 클릭하고 키보드로 타자를 치면 빠르게 검색할 수 있습니다!")
    
    selected_chars, selected_weapons, portrays, resonances, selected_mods = draw_character_slots()
    st.divider()

    st.markdown("### 📝 코멘트 및 영상 (선택 사항)")
    user_comment = st.text_area("💬 파티 운용 팁이나 소감 (최대 100자)", max_chars=100, height=68)
    youtube_url = st.text_input("📺 유튜브 클리어 영상 링크", placeholder="예: https://youtu.be/...")
    
    st.divider()
    st.markdown("### 📸 인증 사진 첨부")

    proof_b64 = get_image_base64("proof_image_help.webp")
    portray_b64 = get_image_base64("portray_help_img.png")

    proof_help_msg = f"""
    **[인증 캡처 예시]** 아래 사진처럼 레이드 결과창 전체가 선명하게 보이도록 캡처해 주세요!

    ![점수 인증 예시](data:image/webp;base64,{proof_b64})
    """

    portray_help_msg = f"""
    **[형상 캡처 예시]** 핀 기능을 이용하여 참가한 4명의 캐릭터가 모두 화면에 나오게 찍어주세요.

    ![형상 인증 예시](data:image/png;base64,{portray_b64})
    """
    
    proof_img = st.file_uploader(
        "클리어 점수 인증 캡처 (필수, 레이드 결과창 사진만 받습니다!)", 
        type=["png", "jpg", "jpeg", "webp"], 
        max_upload_size=10,
        help=proof_help_msg)
    portray_img = st.file_uploader(
        "캐릭터 형상 인증 캡처 (필수, 참가한 캐릭터가 모두 나오게 캡쳐해주세요! 핀 기능을 이용하면 수월합니다.)", 
        type=["png", "jpg", "jpeg", "webp"], 
        max_upload_size=10,
        help=portray_help_msg)
    
    # 🚨 st.form_submit_button 대신 일반 버튼(st.button)으로 교체했습니다!
    submit_btn = st.button("🚀 등록 요청하기", type="primary", width='stretch')
    
    if submit_btn:
        final_nickname = nickname.strip()
        if not final_nickname:
            final_nickname = st.session_state["random_nickname"]
        if not password or score == 0:
            st.error("비밀번호, 점수를 모두 입력해 주세요!")
        elif len(password) > 20:
            st.error("비밀번호는 최대 20자까지 입력 가능합니다!")
        elif proof_img is None or portray_img is None:
            st.error("인증 사진 2장을 모두 첨부해 주세요!")
        elif "🔎검색..." in selected_chars or "🔎검색..." in selected_weapons:
            st.error("파티원 4명의 캐릭터와 의지를 모두 선택해 주세요!")
        else:
            # 🔄 업로드 중 빙글빙글 도는 로딩 애니메이션 띄우기
            with st.spinner("서버로 데이터를 전송 중입니다... 잠시만 기다려주세요!"):
                try:

                    # 업로드된 파일의 공개 주소(URL) 획득
                    proof_url = upload_storage_image(proof_img)
                    portray_url = upload_storage_image(portray_img)

                    # 2. DB 표(Table)에 넣을 데이터 하나로 예쁘게 포장하기
                    # 💡 주의: 왼쪽의 키워드("boss", "score" 등)가 Supabase DB 컬럼명과 완전히 똑같아야 합니다!
                    deck_key, total_portrays = to_analyze_recommended_decks(selected_chars, portrays)

                    deck_code = generate_deck_code(selected_chars, selected_weapons, portrays, resonances, selected_mods)

                    insert_new_record(
                        boss=selected_boss,
                        score=score,
                        nickname=final_nickname,
                        password=password,
                        selected_chars=selected_chars,
                        selected_weapons=selected_weapons,
                        portrays=portrays,
                        resonances=resonances,
                        user_comment=user_comment,
                        youtube_url=youtube_url,
                        proof_url=proof_url,
                        portray_url=portray_url,
                        deck_key=deck_key,
                        total_portrays=total_portrays,
                        selected_mods=selected_mods,
                        deck_code=deck_code
                    )

                    # 4. 성공 알림 및 화면 새로고침
                    st.success("🎉 기록 등록이 완료되었습니다! (관리자 승인 후 게시판에 반영됩니다)")
                    st.session_state.pop("random_nickname", None)
                    import time
                    time.sleep(2) # 2초 동안 성공 메시지를 보여준 뒤
                    st.rerun()    # 화면 새로고침!

                    if "preset_data" in st.session_state:
                        del st.session_state["preset_data"]

                except Exception as e:
                    # 혹시나 에러가 나면 붉은색으로 에러 원인을 알려줍니다.
                    st.error(f"데이터 전송 중 오류가 발생했습니다. 사진을 확인해주세요.")