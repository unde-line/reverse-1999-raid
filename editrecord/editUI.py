import streamlit as st
from services.DB import get_recommended_decks_preset, CHAR_IMG, WEAPON_IMG, CHAR_BLOCKS, PATTERN_DICT, CHAR_REC_MODS
from services.components import sync_resonance

def apply_preset_action(boss_name, deck_type):
    preset = get_recommended_decks_preset(boss_name, deck_type)
    
    if preset:
        chars = preset.get("chars", [])
        weapons = preset.get("weapons", [])
        
        # 💡 핵심: 위젯의 key(char_0, weap_0 등)에 데이터를 다이렉트로 덮어씌웁니다!
        for i in range(4):
            char_name = "🔎검색..." # 기본값 세팅
            # 캐릭터 주입
            if len(chars) > i:
                char_name = chars[i]
                st.session_state[f"char_{i}"] = char_name
            # 의지 주입
            if len(weapons) > i:
                st.session_state[f"weap_{i}"] = weapons[i]
            
            # 공명 레벨 주입 (정석은 10, 고점은 13)
            res_level = 10 if deck_type == "stable" else 13
            st.session_state[f"res_slider_reg_{i}"] = res_level
            st.session_state[f"res_input_reg_{i}"] = res_level
            # ==========================================================
            # 💡 4. [추가] 공명 변조 주입 (캐릭터 DB 연동)
            # ==========================================================
            if char_name != "🔎검색...":
                # CHAR_REC_MODS 딕셔너리에서 해당 캐릭터의 추천 변조를 가져옵니다. (없으면 기본값)
                recommended_mod = CHAR_REC_MODS.get(char_name, "게시하지 않음")
                st.session_state[f"mod_{i}"] = recommended_mod
            else:
                st.session_state[f"mod_{i}"] = "게시하지 않음"
            # ==========================================================

        # 초기화 버튼 표시를 위해 세션에 남겨둠
        st.session_state["preset_data"] = preset
    else:
        st.toast(f"아직 [{boss_name}]의 덱 데이터가 없습니다!", icon="🚨")

def clear_all_inputs_action(original_record=None):
    if "preset_data" in st.session_state:
        del st.session_state["preset_data"]
        
    for i in range(4):
        if original_record:
            # 💡 [수정 모드] 원래 DB에 있던 기록으로 복구!
            st.session_state[f"char_{i}"] = original_record["characters"][i] if i < len(original_record["characters"]) else "🔎검색..."
            st.session_state[f"weap_{i}"] = original_record["weapons"][i] if i < len(original_record["weapons"]) else "🔎검색..."
            st.session_state[f"port_{i}"] = original_record["portrays"][i] if i < len(original_record["portrays"]) else 0
            
            initial_res = original_record.get("resonances", [0,0,0,0])[i] if i < len(original_record.get("resonances", [])) else 0
            st.session_state[f"res_slider_reg_{i}"] = initial_res
            st.session_state[f"res_input_reg_{i}"] = initial_res
            # ==========================================================
            # 💡 [추가] 공명 변조 원본 복구
            # ==========================================================
            mods_list = original_record.get("resonances_mods", ["게시하지 않음"] * 4)
            st.session_state[f"mod_{i}"] = mods_list[i] if i < len(mods_list) else "게시하지 않음"
        else:
            # 💡 [등록 모드] 완전 빈칸으로 초기화!
            st.session_state[f"char_{i}"] = "🔎검색..."
            st.session_state[f"weap_{i}"] = "🔎검색..."
            st.session_state[f"port_{i}"] = 0
            st.session_state[f"res_slider_reg_{i}"] = 0
            st.session_state[f"res_input_reg_{i}"] = 0
            # ==========================================================
            # 💡 [추가] 공명 변조 빈칸 초기화
            # ==========================================================
            st.session_state[f"mod_{i}"] = "게시하지 않음"
        if original_record:
            st.session_state["edit_boss"] = original_record["boss_name"]
            st.session_state["edit_score"] = int(original_record["score"])

def confirm_preset_callback(boss_name, deck_type):
    # '예'를 눌렀을 때 엔진을 가동하고, 대기 상태를 해제합니다.
    apply_preset_action(boss_name, deck_type)
    if "pending_preset" in st.session_state:
        del st.session_state["pending_preset"]

def cancel_preset_callback():
    # '아니요'를 눌렀을 때 대기 상태만 없앱니다.
    if "pending_preset" in st.session_state:
        del st.session_state["pending_preset"]

def confirm_clear_callback():
    # '예'를 누르면 진짜로 다 밀어버리고 대기 상태 해제
    clear_all_inputs_action()
    if "pending_clear" in st.session_state:
        del st.session_state["pending_clear"]

def cancel_clear_callback():
    # '아니요'를 누르면 복구하지 않고 경고창만 닫기
    if "pending_clear" in st.session_state:
        del st.session_state["pending_clear"]

def confirm_clear_callback(original_record=None):
    # original_record를 받아서 엔진으로 넘겨줍니다.
    clear_all_inputs_action(original_record)
    if "pending_clear" in st.session_state:
        del st.session_state["pending_clear"]

# 프리셋 버튼 UI를 그려주는 함수
def draw_preset_buttons(selected_boss, original_record=None):
    st.caption(f"💡 [{selected_boss}] 랭커들의 추천 덱 가져오기")
    btn1, btn2, btn3 = st.columns([2, 2, 1])
    
    with btn1:
        if st.button("🔹 정석 덱 (1,000만)", width='stretch'):
            st.session_state["pending_preset"] = {"boss": selected_boss, "type": "stable", "label": "1,000만"}
            if "pending_clear" in st.session_state:
                del st.session_state["pending_clear"]
    with btn2:
        if st.button("🔸 고점 덱 (3,000만)", width='stretch'):
            st.session_state["pending_preset"] = {"boss": selected_boss, "type": "high", "label": "3,000만"}
            if "pending_clear" in st.session_state:
                del st.session_state["pending_clear"]
    with btn3:
        btn_label = "🔄 초기화" if not original_record else "⏪ 원본 복구"
        if st.button(btn_label, width='stretch'):
            st.session_state["pending_clear"] = True
            if "pending_preset" in st.session_state:
                del st.session_state["pending_preset"]


    # ========================================================
    # 🚨 1번 경고창: 프리셋 덮어쓰기 대기 상태일 때
    # ========================================================
    if "pending_preset" in st.session_state:
        pending = st.session_state["pending_preset"]
        st.warning(f"🚨 **{pending['boss']}**의 **{pending['label']}** 추천 덱으로 바꾸시겠습니까? 작성하셨던 파티 구성 내용은 전부 사라집니다.", icon="⚠️")
        
        conf1, conf2 = st.columns(2)
        with conf1:
            st.button("예 (추천 덱으로 덮어쓰기)", type="primary", width='stretch', 
                      on_click=confirm_preset_callback, args=(pending["boss"], pending["type"]))
        with conf2:
            st.button("아니요 (취소)", width='stretch', on_click=cancel_preset_callback)

    # 🚨 2번 경고창: 초기화 vs 원본 복구
    if st.session_state.get("pending_clear"):
        # 💡 원본 기록 유무에 따라 경고창 메시지도 달라집니다!
        if original_record:
            st.error("🚨 **정말 원본으로 복구하시겠습니까?** 수정 중이던 내용이 모두 사라지고 처음 기록된 상태로 되돌아갑니다.", icon="⏪")
            yes_label = "예 (원본 복구)"
        else:
            st.error("🚨 **정말 초기화하시겠습니까?** 현재 선택된 모든 캐릭터, 의지, 공명 레벨 정보가 전부 초기 상태로 청소됩니다.", icon="🗑️")
            yes_label = "예 (전체 초기화)"
            
        clear1, clear2 = st.columns(2)
        with clear1:
            # args=(original_record,) 를 추가해서 원본 데이터를 콜백으로 넘깁니다!
            st.button(yes_label, type="primary", width='stretch', on_click=confirm_clear_callback, args=(original_record,))
        with clear2:
            st.button("아니요 (취소)", width='stretch', on_click=cancel_clear_callback)

def draw_character_slots():
    """
    4개의 캐릭터 선택 슬롯을 화면에 그리고, 선택된 값들을 반환합니다.
    """
    selected_chars = []
    selected_weapons = []
    portrays = []
    resonances = []
    selected_mods = []
    
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
                st.markdown(f"<div style='text-align: center;'><img src='{WEAPON_IMG[w]}' width='100'></div>", unsafe_allow_html=True)
            
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
                res_level = st.number_input("레벨", min_value=0, max_value=15, key=input_key, on_change=sync_resonance, args=(i, "input", "reg"), label_visibility="collapsed")
            with col3:
                st.markdown(f"<div style='text-align: center; margin-top: 7px;'>/ 15</div>", unsafe_allow_html=True)

            res_level = st.slider("🔮 공명 레벨", min_value=0, max_value=15, step=1, key=slider_key, on_change=sync_resonance, args=(i, "slider", "reg"), label_visibility="collapsed")
            
            if res_level == 0:
                st.caption(f"<div style='text-align: center; text-decoration: bold; font-size: 16px;'>0레벨로 둘 경우, 공명을 게시하지 않습니다.</div>", unsafe_allow_html=True)

            # ==========================================================
            # 💡 5. 공명 변조 선택 (공명 레벨 밑으로 위치 이동!)
            # ==========================================================
            current_mod = "게시하지 않음" # 기본값 세팅
            
            if c != "🔎검색..." and c in CHAR_IMG:
                # 💡 캐릭터의 공명 블록은 무조건 1개! (쉼표 split 생략)
                raw_block = CHAR_BLOCKS.get(c) 
                
                if raw_block: 
                    char_block = raw_block.strip() # 예: "+", "z" 등

                    available_patterns = PATTERN_DICT.get(char_block, [])
                    
                    block_options = ["게시하지 않음"]
                    
                    # 💡 PATTERN_DICT를 전부 뒤져서, 캐릭터의 블록 모양과 일치하는 패턴을 모두 가져옵니다.
                    for pat in available_patterns:
                        b_name = pat["name"]
                        block_options.append(b_name)
                    
                    
                    is_locked = (res_level < 10)
                    
                    mod_selection = st.selectbox(
                        "🧩 공명 변조", 
                        block_options, 
                        key=f"mod_{i}",
                        disabled=is_locked,
                        help="공명 레벨 10 이상부터 변조를 설정할 수 있습니다." if is_locked else None
                    )
                    
                    # 유저가 고른 값 그대로 저장
                    current_mod = mod_selection 

                    # 💡 이미지 출력
                    if not is_locked and current_mod != "게시하지 않음":
                        mod_img_url = None
                        # 고른 이름과 일치하는 URL을 방에서 찾습니다.
                        for pat in available_patterns:
                            if pat["name"] == current_mod:
                                mod_img_url = pat["url"]
                                break
                                
                        st.markdown(f"<div style='text-align: center; margin-top: 5px;'><img src='{mod_img_url}' width='100' style='border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'></div>", unsafe_allow_html=True)
            # ==========================================================

            selected_chars.append(c)
            selected_weapons.append(w)
            portrays.append(p)
            resonances.append(res_level)
            selected_mods.append(current_mod)

    # 💡 4명의 캐릭터 정보가 담긴 4개의 리스트를 밖으로 던져줍니다!
    return selected_chars, selected_weapons, portrays, resonances, selected_mods