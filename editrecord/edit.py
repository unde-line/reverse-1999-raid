import streamlit as st
from services.DB import edit_storage_image, edit_data
from services.utils import to_analyze_recommended_decks, generate_deck_code
from services.config import CURRENT_SEASON_BOSSES
from editrecord.editUI import draw_character_slots, draw_preset_buttons



@st.dialog("✏️ 기록 전면 수정", width="large")
def show_edit_popup(record):

    if st.session_state.get("current_edit_id") != record["id"]:
        st.session_state["current_edit_id"] = record["id"]
        
        # 이전 팝업에서 남았을지 모르는 대기 상태 및 프리셋 데이터 청소
        st.session_state.pop("pending_preset", None)
        st.session_state.pop("pending_clear", None)
        st.session_state.pop("preset_data", None)

        # 💡 [추가] 팝업창이 처음 열릴 때, 보스와 점수의 원본 값을 세션에 미리 심어둡니다!
        st.session_state["edit_boss"] = record["boss_name"]
        st.session_state["edit_score"] = int(record["score"])
        
        # 4명의 기존 캐릭터, 의지, 형상, 공명 정보를 컴포넌트 키 형식에 맞춰 강제 주입
        for i in range(4):
            st.session_state[f"char_{i}"] = record["characters"][i] if i < len(record["characters"]) else "🔎검색..."
            st.session_state[f"weap_{i}"] = record["weapons"][i] if i < len(record["weapons"]) else "🔎검색..."
            st.session_state[f"port_{i}"] = record["portrays"][i] if i < len(record["portrays"]) else 0
            
            initial_res = record["resonances"][i] if i < len(record.get("resonances", [])) else 0
            st.session_state[f"res_slider_reg_{i}"] = initial_res
            st.session_state[f"res_input_reg_{i}"] = initial_res

            # ==========================================================
            # 💡 [추가] 공명 변조 데이터 주입
            # 혹시라도 DB에 배열이 없거나 짧을 경우를 대비해 안전장치(기본값: 게시하지 않음)를 겁니다.
            # ==========================================================
            mods_list = record.get("resonances_mods", [])
            initial_mod = mods_list[i] if i < len(mods_list) else "게시하지 않음"
            st.session_state[f"mod_{i}"] = initial_mod

    st.warning(f"[{record['boss_name']}] 기록의 모든 내용을 수정합니다.")
    pwd_input = st.text_input("🔒 글 비밀번호 (권한 확인용)", type="password", max_chars=20)
    
    st.divider()
    
    # 1. 기본 정보 세팅
    col1, col2 = st.columns(2)
    boss_list = CURRENT_SEASON_BOSSES
    # 기존 보스 이름이 리스트의 몇 번째인지 찾습니다.
    default_boss_idx = boss_list.index(record["boss_name"]) if record["boss_name"] in boss_list else 0
        
    with col1:
        new_boss = st.selectbox("👹 보스 선택", boss_list, key="edit_boss")
    with col2:
        new_score = st.number_input("🏆 점수", min_value=0, step=10000, key="edit_score")

    draw_preset_buttons(new_boss, original_record=record)
    st.divider()
    st.markdown("### 👥 파티 구성 수정")
    
    new_chars, new_weapons, new_portrays, new_resonances, new_selected_mods = draw_character_slots()

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
                    final_proof_url = record.get("proof_url", "") 
                    final_portray_url = record.get("portray_proof_url", "")

                    if new_proof_img is not None:
                        new_proof_url = edit_storage_image(final_proof_url, new_proof_img)
                    else:
                        new_proof_url = final_proof_url

                    if new_portray_img is not None:
                        new_portray_url = edit_storage_image(final_portray_url, new_portray_img)
                    else:
                        new_portray_url = final_portray_url
                    
                    deck_key, total_portrays = to_analyze_recommended_decks(new_chars, new_portrays)

                    new_deck_code = generate_deck_code(new_chars, new_weapons, new_portrays, new_resonances, new_selected_mods)

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
                        new_portray_url=new_portray_url,
                        new_deck_key=deck_key,
                        new_total_portrays=total_portrays,
                        new_selected_mods=new_selected_mods,
                        new_deck_code=new_deck_code
                    )
                    
                    st.success("🎉 모든 정보가 완벽하게 수정되었습니다!")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"수정 중 오류가 발생했습니다: {e}")