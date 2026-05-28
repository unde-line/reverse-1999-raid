import streamlit as st
from services.DB import CHAR_IMG, WEAPON_IMG, CHAR_BLOCKS, PATTERN_DICT, code_to_deck
from services.components import sync_resonance
from services.utils import get_image_base64
from editrecord.editsystem import confirm_clear_callback, confirm_preset_callback, cancel_clear_callback, cancel_preset_callback
from services.config import CURRENT_SEASON_BOSSES

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
            st.button("예 (추천 덱으로 덮어쓰기)", type="primary", width='stretch')
            confirm_preset_callback(pending["boss"], pending["type"])
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

def draw_record_form(mode="insert", default_data=None, record_id=""):
    """
    등록/수정 UI를 통합해서 그려주고, 
    유저가 입력한 데이터(raw_data, images)와 제출 버튼 클릭 여부(submit_btn)를 반환합니다.
    """
    if default_data is None:
        default_data = {}
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
    st.markdown("### 👹 보스 및 기본 정보")
    col1, col2 = st.columns(2)
    
    # 💡 보스 초기값 세팅 (기존 보스가 리스트에 없으면 0번 인덱스)
    boss_list = CURRENT_SEASON_BOSSES
    boss_val = default_data.get("boss")
    boss_idx = boss_list.index(boss_val) if boss_val in boss_list else 0
    
    with col1:
        boss = st.selectbox("보스 선택", boss_list, index=boss_idx, key=f"boss_{mode}_{record_id}")
    with col2:
        score = st.number_input("🏆 점수", min_value=0, step=10000, value=default_data.get("score", 0), key=f"score_{mode}_{record_id}")

    draw_preset_buttons(boss) # 프리셋 버튼
    
    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        if mode == "insert":
            nickname = st.text_input("👤 닉네임 (최대 10자)", max_chars=10, key="nick_insert", placeholder=st.session_state.get("random_nickname", ""))
            if not nickname.strip():
                nickname = st.session_state.get("random_nickname", "")
        else:
            # 수정 모드일 때는 닉네임 변경 불가 처리 (보기 전용)
            st.text_input("👤 닉네임", value=default_data.get("nickname", ""), disabled=True, key=f"nick_edit_{record_id}")
            nickname = default_data.get("nickname", "")
            
    with col4:
        pwd_label = "🔒 글 비밀번호 (수정/삭제용)" if mode == "insert" else "🔒 글 비밀번호 (권한 확인용)"
        password = st.text_input(pwd_label, type="password", max_chars=20, key=f"pwd_{mode}_{record_id}")

    st.divider()
    st.markdown("### 👥 파티 구성")
    st.caption("💡 팁: 캐릭터와 의지 칸을 클릭하고 키보드로 타자를 치면 빠르게 검색할 수 있습니다!")
    
    # 캐릭터 슬롯 컴포넌트 호출
    selected_chars, selected_weapons, portrays, resonances, selected_mods = draw_character_slots()

    st.divider()
    st.markdown("### 📝 코멘트 및 영상")
    comment = st.text_area("💬 파티 운용 팁 (최대 100자)", value=default_data.get("comment", ""), max_chars=100, key=f"comment_{mode}_{record_id}")
    youtube = st.text_input("📺 유튜브 클리어 영상 링크", value=default_data.get("youtube", ""), key=f"yt_{mode}_{record_id}")

    st.divider()
    st.markdown("### 📸 인증 사진 첨부")

    proof_b64 = get_image_base64("proof_image_help.webp")
    portray_b64 = get_image_base64("portray_help_img.webp")

    proof_help_msg = f"""
    **[인증 캡처 예시]** 아래 사진처럼 레이드 결과창 전체가 선명하게 보이도록 캡처해 주세요!

    ![점수 인증 예시](data:image/webp;base64,{proof_b64})
    """

    portray_help_msg = f"""
    **[형상 캡처 예시]** 핀 기능을 이용하여 참가한 4명의 캐릭터가 모두 화면에 나오게 찍어주세요.

    ![형상 인증 예시](data:image/webp;base64,{portray_b64})
    """
    
    if mode == "insert":
        # 등록 시에는 사진 필수로 받음 + 도움말 표시
        proof_img = st.file_uploader("클리어 점수 인증 캡처 (필수)", type=["png", "jpg", "jpeg", "webp"], key="proof_insert", help=proof_help_msg, max_upload_size=10)
        portray_img = st.file_uploader("캐릭터 형상 인증 캡처 (필수)", type=["png", "jpg", "jpeg", "webp"], key="portray_insert", help= portray_help_msg, max_upload_size=10)
        btn_label = "🚀 등록 요청하기"
    else:
        # 수정 시에는 사진 선택 (안 올리면 기존 것 유지)
        st.caption("💡 새로운 사진을 업로드하지 않으면 **기존에 올렸던 사진이 그대로 유지**됩니다!")
        proof_img = st.file_uploader("새로운 클리어 점수 인증 캡처", type=["png", "jpg", "jpeg", "webp"], key=f"proof_edit_{record_id}", max_upload_size=10)
        portray_img = st.file_uploader("새로운 캐릭터 형상 인증 캡처", type=["png", "jpg", "jpeg", "webp"], key=f"portray_edit_{record_id}", max_upload_size=10)
        btn_label = "💾 모든 정보 수정하기"

    # 최종 제출 버튼
    submit_btn = st.button(btn_label, type="primary", width='stretch')

    # 💡 흩어져 있는 변수들을 다 예쁘게 모아서 리턴합니다!
    raw_data = {
        "boss": boss, "score": score, "nickname": nickname, "password": password,
        "chars": selected_chars, "weapons": selected_weapons, "portrays": portrays,
        "resonances": resonances, "mods": selected_mods, "comment": comment, "youtube": youtube
    }
    images = {"proof": proof_img, "portray": portray_img}

    return submit_btn, raw_data, images