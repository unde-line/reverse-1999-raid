import streamlit as st
from services.DB import supabase, CHAR_IMG, WEAPON_IMG, edit_storage_image, edit_data
from services.components import sync_resonance



@st.dialog("✏️ 기록 전면 수정", width="large")
def show_edit_popup(record):
    st.warning(f"[{record['boss_name']}] 기록의 모든 내용을 수정합니다.")
    pwd_input = st.text_input("🔒 글 비밀번호 (권한 확인용)", type="password", max_chars=20)
    
    st.divider()
    
    # 1. 기본 정보 세팅
    col1, col2 = st.columns(2)
    boss_list = [ "괴멸의 궤도", "급성 선홍증", "신앙의 이동"]
    # 기존 보스 이름이 리스트의 몇 번째인지 찾습니다.
    default_boss_idx = boss_list.index(record["boss_name"]) if record["boss_name"] in boss_list else 0
        
    with col1:
        new_boss = st.selectbox("👹 보스 선택", boss_list, index=default_boss_idx)
    with col2:
        new_score = st.number_input("🏆 점수", min_value=0, step=10000, value=int(record["score"]))

    st.divider()
    st.markdown("### 👥 파티 구성 수정")
    
    char_list = ["🔎검색..."] + list(CHAR_IMG.keys()) 
    weapon_list = ["🔎검색..."] + list(WEAPON_IMG.keys())
    portray_list = [0, 1, 2, 3, 4, 5]
    

    new_chars = []
    new_weapons = []
    new_portrays = []
    new_resonances = []
    
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            st.markdown(f"**[{i+1}픽]**")
            current_resonance = f"res_master_{i}_{record['id']}"

            fields = [
            ("characters", "👤 캐릭터", char_list, new_chars, 0),
            ("weapons", "⚔️ 의지", weapon_list, new_weapons, 0),
            ("portrays", "🧩 형상 돌파", portray_list, new_portrays, 0)
            ]
            # 묶어둔 설정값을 하나씩 꺼내면서 UI를 그립니다.
            for db_key, label, options, target_list, default_idx in fields:
                
                # 1. DB에서 기존 값 가져오기
                old_val = record[db_key][i]
                
                # 2. 인덱스 찾기 (없으면 fallback 기본값)
                current_idx = options.index(old_val) if old_val in options else default_idx
                
                # 3. 셀렉트박스 렌더링 (key에 db_key를 넣어 고유하게 만듦)
                selected_val = st.selectbox(
                    label, 
                    options, 
                    index=current_idx, 
                    key=f"edit_{db_key}_{i}_{record['id']}"
                )
                
                # 4. 새 리스트에 선택된 값 추가
                target_list.append(selected_val)
            # 공명은 슬라이더로 따로 빼서 처리
            slider_key = f"res_slider_edit_{i}_{record['id']}"
            input_key = f"res_input_edit_{i}_{record['id']}"

            if slider_key not in st.session_state:
                initial_val = record.get("resonances", [0, 0, 0, 0])[i]
                st.session_state[slider_key] = initial_val
                st.session_state[input_key] = initial_val

            space, col2, col3, space2 = st.columns([1, 1, 1, 1])
            with space:
                st.markdown(f"<div style='margin-top: 9px; font-size: 15px;'>🔮 공명</div>", unsafe_allow_html=True)
            with col2:
                res_level=st.number_input( "레벨", min_value=0, max_value=15, key=input_key, on_change=sync_resonance, args=(i, "input", "edit", record['id']), label_visibility="collapsed")
            with col3:
                st.markdown(f"<div style='text-align: center; margin-top: 7px;'>/ 15</div>", unsafe_allow_html=True)

            res_level =st.slider("🔮 공명 레벨", min_value=0, max_value=15, step=1, key=slider_key, on_change=sync_resonance, args=(i, "slider", "edit", record['id']), label_visibility="collapsed")
            new_resonances.append(res_level)
            if res_level == 0:
                st.caption(f"<div style='text-align: center; text-decoration: bold; font-size: 16px;'>0레벨로 둘 경우, 공명을 게시하지 않습니다.</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📝 코멘트 및 영상 수정")
    # DB에 값이 비어있을(None) 경우를 대비해 안전하게 빈 칸("")으로 처리합니다.
    new_comment = st.text_area("💬 파티 운용 팁 (최대 100자)", value=record.get("comment") or "", max_chars=100)
    new_youtube = st.text_input("📺 유튜브 클리어 영상 링크", value=record.get("video_url") or "")

    st.divider()
    st.markdown("### 📸 인증 사진 수정 (선택 사항)")
    st.caption("💡 팁: 새로운 사진을 업로드하지 않으면 **기존에 올렸던 사진이 그대로 유지**됩니다!")
    
    new_proof_img = st.file_uploader("새로운 클리어 점수 인증 캡처", type=["png", "jpg", "jpeg", "webp"], key=f"edit_proof_{record['id']}", max_upload_size=10)
    new_portray_img = st.file_uploader("새로운 캐릭터 형상 인증 캡처", type=["png", "jpg", "jpeg", "webp"], key=f"edit_portray_{record['id']}", max_upload_size=10)

    submit_btn = st.button("💾 모든 정보 수정하기", type="primary", width='stretch')
    
    if submit_btn:
        if pwd_input != record["password"]:
            st.error("비밀번호가 일치하지 않습니다!")
        elif len(pwd_input) > 20:
            st.error("비밀번호는 최대 20자까지 입력 가능합니다!")
        elif "🔎검색..." in new_chars or "🔎검색..." in new_weapons:
            st.error("파티원 4명의 캐릭터와 의지를 모두 선택해 주세요!")
        else:
            with st.spinner("수정된 데이터를 서버에 덮어씌우는 중입니다..."):
                try:
                    # db에 값이 비어있을 수 있으니 .get()으로 안전하게 가져옵니다.
                    final_proof_url = record.get("proof_url", "") #TODO: 함수로 옮겨서 정리하기 register.py에도 똑같은 코드가 있어서 중복이 좀 있습니다.
                    final_portray_url = record.get("portray_proof_url", "")

                    if new_proof_img is not None:
                        new_proof_url = edit_storage_image(final_proof_url, new_proof_img)
                    else:
                        new_proof_url = final_proof_url

                    if new_portray_img is not None:
                        new_portray_url = edit_storage_image(final_portray_url, new_portray_img)
                    else:
                        new_portray_url = final_portray_url

                    edit_data(
                        record_id=record["id"],
                        new_boss=new_boss,
                        new_score=new_score,
                        new_chars=new_chars,
                        new_weapons=new_weapons,
                        new_portrays=new_portrays,
                        new_resonances=new_resonances,
                        new_comment=new_comment,
                        new_youtube=new_youtube,
                        new_proof_url=new_proof_url,
                        new_portray_url=new_portray_url
                    )
                    
                    st.success("🎉 모든 정보가 완벽하게 수정되었습니다!")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"수정 중 오류가 발생했습니다: {e}")