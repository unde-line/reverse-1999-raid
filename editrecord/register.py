import streamlit as st
from services.DB import CHAR_IMG, WEAPON_IMG
from services.components import sync_resonance
from services.DB import upload_storage_image, insert_new_record

@st.dialog("✨ 새로운 레이드 기록 등록", width="large")
def show_register_popup():
    st.write("리버스: 1999 레이드 기록을 등록해 주세요. (관리자 승인 후 반영됩니다)")
    

    # 1. 기본 정보
    col1, col2 = st.columns(2)
    with col1:
        boss = st.selectbox("👹 보스 선택", ["괴멸의 궤도", "급성 선홍증", "신앙의 이동"])
    with col2:
        score = st.number_input("🏆 점수", min_value=0, step=10000, format="%d")
        
    col3, col4 = st.columns(2)
    with col3:
        nickname = st.text_input("👤 닉네임 (최대 10자)", max_chars=10)
    with col4:
        password = st.text_input("🔒 글 비밀번호 (수정/삭제용)", type="password", max_chars=20)

    st.divider()
    st.markdown("### 👥 파티 구성")
    st.caption("💡 팁: 캐릭터와 의지 칸을 클릭하고 키보드로 타자를 치면 빠르게 검색할 수 있습니다!")
    
    selected_chars = []
    selected_weapons = []
    portrays = []
    resonances = []
    
    char_list = ["🔎검색..."] + list(CHAR_IMG.keys()) 
    weapon_list = ["🔎검색..."] + list(WEAPON_IMG.keys())
    portray_list = [0, 1, 2, 3, 4, 5]
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.markdown(f"**[{i+1}픽]**")

            
            c = st.selectbox("👤 캐릭터", char_list, key=f"char_{i}")
            if c != "🔎검색..." and c in CHAR_IMG:
                st.markdown(f"<div style='text-align: center;'><img src='{CHAR_IMG[c]}' width='60'></div>", unsafe_allow_html=True)
            
            w = st.selectbox("⚔️ 의지", weapon_list, key=f"weap_{i}")
            if w != "🔎검색..." and w in WEAPON_IMG:
                st.markdown(f"<div style='text-align: center;'><img src='{WEAPON_IMG[w]}' width='60'></div>", unsafe_allow_html=True)
            
            p = st.selectbox("🧩 형상 돌파", portray_list, key=f"port_{i}")

            slider_key = f"res_slider_reg_{i}"
            input_key = f"res_input_reg_{i}"

            if slider_key not in st.session_state:
                st.session_state[slider_key] = 0
                st.session_state[input_key] = 0

            space, col2, col3, space2 = st.columns([1, 1, 1, 1])
            with space:
                st.markdown(f"<div style='margin-top: 9px; font-size: 15px;'>🔮 공명</div>", unsafe_allow_html=True)
            with col2:
                res_level=st.number_input( "레벨", min_value=0, max_value=15, key=f"res_input_reg_{i}", on_change=sync_resonance, args=(i, "input", "reg"), label_visibility="collapsed")
            with col3:
                st.markdown(f"<div style='text-align: center; margin-top: 7px;'>/ 15</div>", unsafe_allow_html=True)

            res_level =st.slider("🔮 공명 레벨", min_value=0, max_value=15, step=1, key=f"res_slider_reg_{i}", on_change=sync_resonance, args=(i, "slider", "reg"), label_visibility="collapsed")

            
            selected_chars.append(c)
            selected_weapons.append(w)
            portrays.append(p)
            resonances.append(res_level)

            if res_level == 0:
                st.caption(f"<div style='text-align: center; text-decoration: bold; font-size: 16px;'>0레벨로 둘 경우, 공명을 게시하지 않습니다.</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📝 코멘트 및 영상 (선택 사항)")
    user_comment = st.text_area("💬 파티 운용 팁이나 소감 (최대 100자)", max_chars=100, height=68)
    youtube_url = st.text_input("📺 유튜브 클리어 영상 링크", placeholder="예: https://youtu.be/...")
    
    st.divider()
    st.markdown("### 📸 인증 사진 첨부")
    
    proof_img = st.file_uploader("클리어 점수 인증 캡처 (필수, 레이드 결과창 사진만 받습니다!)", type=["png", "jpg", "jpeg", "webp"], max_upload_size=10)
    portray_img = st.file_uploader("캐릭터 형상 인증 캡처 (필수, 참가한 캐릭터가 모두 나오게 캡쳐해주세요! 핀 기능을 이용하면 수월합니다.)", type=["png", "jpg", "jpeg", "webp"], max_upload_size=10)
    
    # 🚨 st.form_submit_button 대신 일반 버튼(st.button)으로 교체했습니다!
    submit_btn = st.button("🚀 등록 요청하기", type="primary", width='stretch')
    
    if submit_btn:
        if not nickname or not password or score == 0:
            st.error("닉네임, 비밀번호, 점수를 모두 입력해 주세요!")
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
                    insert_new_record(
                        boss=boss,
                        score=score,
                        nickname=nickname,
                        password=password,
                        selected_chars=selected_chars,
                        selected_weapons=selected_weapons,
                        portrays=portrays,
                        resonances=resonances,
                        user_comment=user_comment,
                        youtube_url=youtube_url,
                        proof_url=proof_url,
                        portray_url=portray_url
                    )

                    # 4. 성공 알림 및 화면 새로고침
                    st.success("🎉 기록 등록이 완료되었습니다! (관리자 승인 후 게시판에 반영됩니다)")
                    import time
                    time.sleep(2) # 2초 동안 성공 메시지를 보여준 뒤
                    st.rerun()    # 화면 새로고침!

                except Exception as e:
                    # 혹시나 에러가 나면 붉은색으로 에러 원인을 알려줍니다.
                    st.error(f"데이터 전송 중 오류가 발생했습니다. 사진을 확인해주세요.")