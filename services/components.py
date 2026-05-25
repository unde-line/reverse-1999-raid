import streamlit as st
from services.DB import CHAR_IMG, WEAPON_IMG, PATTERN_DICT, CHAR_BLOCKS
import html
from services.utils import get_css_text

css_text = get_css_text('services/components.css')  # CSS 텍스트를 캐싱된 함수로 가져오기

def build_character_images(characters):
    return "".join(
        f'<img src="{CHAR_IMG[char]}">'
        for char in characters[:4]
    )

def build_rank_html(real_rank):
    if real_rank is None:
        return "", "0px"
    
    if isinstance(real_rank, int) or (isinstance(real_rank, str) and real_rank.isdigit()):
        return f"#{real_rank}", "0px"
    else:
        return real_rank, "0px"


def draw_ranking_card(item, bg_url, real_rank=None):
    chars_html = build_character_images(item.get("characters", []))
    rank_html, nickname_margin = build_rank_html(real_rank)
    nickname = html.escape(item['nickname'])  # 닉네임에 특수문자가 있을 때 HTML 이스케이프 처리
    score = html.escape(f"{item['score']:,} 점")  # 점수도 마찬가지로 이스케이프 처리
    st.markdown(css_text, unsafe_allow_html=True)

    card_html = f"""
    <div class="ranking-card" style="background: linear-gradient(to right, rgba(14, 17, 23, 0.95) 25%, rgba(14, 17, 23, 0.4) 70%, rgba(14, 17, 23, 0) 100%), url('{bg_url}');">
        <div class="card_info">
            <div class="rank_name_wrap">
                <h4 class="rank_number">{rank_html}</h4>
                <div class = "nickname_wrap">
                    <strong class="nickname" style="margin-left: {nickname_margin};">{nickname}</strong>
                    </div>
            </div>
            <h5 class="score">{score}</h5>
        </div>
        <div class="card-chars">{chars_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def draw_character_card(record):
    st.markdown(css_text, unsafe_allow_html=True)
    st.markdown('<div class="deck-container">', unsafe_allow_html=True)
            
    img_cols = st.columns(4)
    for i in range(4):
        with img_cols[i]:
            st.image(CHAR_IMG[record['characters'][i]], width='stretch')
                
            portray_val = record['portrays'][i] 
            reso_val = record['resonances'][i]  

            # 💡 안전장치: 예전 데이터에 변조 컬럼이 비어있을 경우를 대비해 '게시하지 않음'를 기본값으로 가져옵니다.
            mod_val = record.get('resonances_mods', ["게시하지 않음", "게시하지 않음", "게시하지 않음", "게시하지 않음"])[i]

            if reso_val == 0:
                reso_text = "공명 게시하지 않음"
            else:
                reso_text = f"공명 {reso_val}레벨"
                
            if portray_val == 0:
                portray_text = "명함"
            else:
                portray_text = f"{portray_val} 형상"
                
            info_text = f"{portray_text} / {reso_text}"
            st.markdown(f"<div class='porreso'>{info_text}</div>", unsafe_allow_html=True)
                
            st.image(WEAPON_IMG[record['weapons'][i]], width='stretch')

            # ==========================================================
            # 💡 2. 공명 변조 아이콘 표시 (공명 10레벨 이상일 때만)
            # ==========================================================
            if reso_val >= 10:
                char_name = record['characters'][i]
                char_block = CHAR_BLOCKS.get(char_name, "").strip()
                
                mod_img_url = None
                
                # 💡 해당 기호의 방(리스트)에 들어가서, 이름이 일치하는 URL을 찾습니다.
                if char_block in PATTERN_DICT:
                    for pat in PATTERN_DICT[char_block]:
                        if pat["name"] == mod_val:
                            mod_img_url = pat["url"]
                            break
                
                # URL을 성공적으로 찾았다면 그려줍니다!
                if mod_img_url:
                    mod_html = f"""
                    <div style='margin-top: 6px; margin-bottom: 6px; height: 110px; display: flex; justify-content: center; align-items: center;' title='공명 변조: {mod_val}'>
                        <img src='{mod_img_url}' style='width: 100px; max-height: 100px; object-fit: contain; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                    </div>
                    """
                    st.markdown(mod_html, unsafe_allow_html=True)
                    st.markdown(f"<div class='porreso'>{mod_val}</div>", unsafe_allow_html=True)
                elif reso_val >= 10 and mod_val == "게시하지 않음":
                    st.markdown(f"<div class='porreso'>공명 변조 게시하지 않음</div>", unsafe_allow_html=True)
                else:
                    debug_msg = f"""
                    <div style='color: #FF4B4B; font-size: 11px; text-align: center; margin-top: 10px; line-height: 1.2;'>
                        🚨 매칭 실패<br>
                        이름: {char_name}<br>
                        블록: [{char_block}]<br>
                        변조: {mod_val}
                    </div>
                    """
                    st.markdown(debug_msg, unsafe_allow_html=True)

                
        st.markdown('</div>', unsafe_allow_html=True)


def get_paginated_data(data, page_key, items_per_page=10):
    """
    전체 데이터를 받아서 현재 페이지에 맞는 데이터만 잘라서 돌려주는 함수
    """
    if not data:
        return [], 0, 1, 1

    total_pages = max(1, (len(data) - 1) // items_per_page + 1)
    current_page = st.session_state.get(page_key, 1)

    # 방어 로직: 검색 필터링 등으로 페이지가 초과되었을 때 안전하게 막아줌
    if current_page > total_pages:
        current_page = total_pages
        st.session_state[page_key] = current_page

    start_idx = (current_page - 1) * items_per_page
    paginated_data = data[start_idx : start_idx + items_per_page]

    return paginated_data, start_idx, current_page, total_pages

def draw_pagination_buttons(page_key, current_page, total_pages):
    """
    하단에 ⬅️ 이전 / 다음 ➡️ 버튼 UI를 그려주는 함수
    """
    st.write("---")
    page_cols = st.columns([1, 2, 1])
    
    if page_cols[0].button("⬅️ 이전", key=f"prev_{page_key}", width='stretch', disabled=(current_page <= 1)):
        st.session_state[page_key] -= 1
        st.rerun()
    
    page_cols[1].markdown(f"<div style='text-align: center; padding-top: 5px;'><b>{current_page} / {total_pages} 페이지</b></div>", unsafe_allow_html=True)
    
    if page_cols[2].button("다음 ➡️", key=f"next_{page_key}", width='stretch', disabled=(current_page >= total_pages)):
        st.session_state[page_key] += 1
        st.rerun()

def draw_search_bar(label, options, search_key, placeholder="검색어 입력...", page_keys_to_reset=None):
    """
    자동완성 검색창을 그리고, 검색어가 변경되면 지정된 페이지 번호들을 1로 돌려주는 만능 위젯
    """
    saved_val = st.session_state.get(search_key)
    default_index = None
    if saved_val and saved_val in options:
        default_index = options.index(saved_val)
    
    # 1. 셀렉트박스 렌더링 (각 검색창마다 고유한 key를 갖도록 설정)
    selected_val = st.selectbox(
        label,
        options=options,
        index=default_index,
        placeholder=placeholder,
        key=f"widget_{search_key}" 
    )

    # 2. 검색어 변경 감지용 세션 초기화
    last_val_key = f"last_{search_key}"
    if last_val_key not in st.session_state:
        st.session_state[last_val_key] = None

    # 3. 검색어가 이전과 달라졌는지 감지!
    if selected_val != st.session_state[last_val_key]:
        st.session_state[last_val_key] = selected_val
        
        # 4. 초기화해달라고 요청받은 페이지 변수들이 있다면 전부 1로 리셋
        if page_keys_to_reset:
            for p_key in page_keys_to_reset:
                if p_key in st.session_state:
                    st.session_state[p_key] = 1
                    
    # 최종적으로 유저가 선택한 검색어 반환
    return selected_val

def sync_resonance(char_idx, source, context="reg", record_id=None):
    id_part = f"_{record_id}" if record_id else ""

    slider_key = f"res_slider_{context}_{char_idx}{id_part}"
    input_key = f"res_input_{context}_{char_idx}{id_part}"

    if source == "slider":
        # 슬라이더를 건드렸으면 그 값을 마스터에 덮어씀
        new_val = st.session_state.get(slider_key)
    else:  # source == "input"
        # 입력칸을 건드렸으면 그 값을 마스터에 덮어씀
        new_val = st.session_state.get(input_key)
    if new_val is not None:
        st.session_state[slider_key] = new_val # 슬라이더 가방 업데이트
        st.session_state[input_key] = new_val  # 입력칸 가방 업데이트

def go_to_detail_page(item, prev_page, boss_name):
    item['boss_name'] = boss_name
    st.session_state.selected_record = item  # 선택한 기록을 세션에 저장
    st.session_state.previous_page = prev_page  # 이전 페이지 정보도 저장
    
    st.switch_page("pages/detail.py")  # 상세 페이지로 이동 