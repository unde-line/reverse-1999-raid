import streamlit as st 
import services.DB
from services.config import BOSS_BG_URLS, CURRENT_SEASON_BOSSES
from services.components import draw_ranking_card, get_paginated_data, draw_pagination_buttons, draw_search_bar, go_to_detail_page
from services.utils import assign_global_ranks, filter_records, load_css



def rank_page_display(): 
    # ----------------------------------------
    # [화면 A] 랭킹 리스트 화면
    # ----------------------------------------
    board_data = services.DB.load_board_data()    
        # 데이터베이스에 있는 캐릭터 이름만 모아서 리스트를 만듭니다 ('전체 보기' 삭제!)
    all_characters = {char for records in board_data.values() for r in records for char in r.get("characters", [])}
    char_options = sorted(list(all_characters))

    st.title("📊 레이드 랭킹 게시판")
    load_css('ranking/rankingpage.css')

    reset_keys = [f"page_{boss}" for boss in CURRENT_SEASON_BOSSES]  # 검색어가 바뀌면 페이지도 1로 초기화하기 위한 키 리스트

    search_char = draw_search_bar(
        label="🔍 캐릭터 검색 (클릭하거나 직접 타이핑하세요!): ",
        options=char_options, 
        search_key="search_char",
        placeholder="예: 투스페어리, 곡랑...", # 빈칸일 때 희미하게 보이는 안내 문구입니다.
        page_keys_to_reset=reset_keys
    )

    st.write("---")
    
    tabs = st.tabs(CURRENT_SEASON_BOSSES)

   

    for idx, tab in enumerate(tabs):

        with tab:
            boss_name = CURRENT_SEASON_BOSSES[idx]
            boss_records = board_data.get(boss_name, [])
            if not boss_records:
                # 데이터가 텅 비었을 때 화면에 보여줄 예쁜 안내문
                st.info("아직 등록된 랭킹 기록이 없습니다. 첫 번째 기록의 주인공이 되어보세요!")
                continue
            # 데이터가 있을 때만 정렬하고 화면에 그립니다.
            ranked_data = assign_global_ranks(boss_records)
            filtered_data = filter_records(ranked_data, search_char=search_char)
            if not filtered_data:
                st.warning(f"'{search_char}' 캐릭터가 포함된 기록이 없습니다.")
                continue

            page_key=f"page_{boss_name}"
            paginated_data, start_idx, current_page, total_pages = get_paginated_data(filtered_data, page_key)
            # 화면에 그리기

            for rank_idx, item in enumerate(paginated_data):
                real_rank = start_idx + rank_idx + 1
                bg_url = BOSS_BG_URLS.get(boss_name.strip(), "https://images.unsplash.com/photo-1604014237800-1c9102c219da?q=80&w=600")
                draw_ranking_card(item, bg_url=bg_url, real_rank=real_rank)

                # 3. 버튼 끌어올리기 마커 및 버튼 코드는 기존과 동일하게 유지!

                st.markdown('<div class="btn-pull-up-marker"></div>', unsafe_allow_html=True)
                btn_cols = st.columns([3, 1])
                with btn_cols[1]:
                    if st.button("상세 보기", key=f"btn_{boss_name}_{item['nickname']}_{real_rank}", width='stretch'):
                        go_to_detail_page(item, "pages/rank.py", boss_name)
                        
            draw_pagination_buttons(page_key, current_page, total_pages)

