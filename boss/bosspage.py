

import streamlit as st
from services.DB import get_character_pickrate, get_recommended_decks, get_hall_of_fame_data, CHAR_IMG, WEAPON_IMG, call_records
from services.config import BOSS_BG_URLS
from services.components import draw_ranking_card, go_to_detail_page


def boss_page_display(boss_name=None):
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.pop("current_boss", None)
        st.switch_page("pages/menu.py")
    
    recommended_decks = get_recommended_decks(boss_name)
    character_pickrates = get_character_pickrate(boss_name)
    hof_data = get_hall_of_fame_data(boss_name)

    st.title(f"👹 {boss_name}")
    st.caption("*본 통계는 공식 통계가 아니며, 사이트 내 등록된 정보들로만 근거로 산정하여 산출한 통계입니다.")

    # ==========================================
    # 1. 상단 보스 정보 & Top 3 캐릭터 카드
    # ==========================================
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(BOSS_BG_URLS.get(boss_name, "https://via.placeholder.com/300x300?text=Boss+Image"), width='stretch')
            
        with col2:
            st.subheader("💡 보스 기믹 및 설명")
            st.write("3.5 버전 이후 업데이트 예정입니다.")
            
            st.divider() # 가로줄
            
            st.subheader("👑 가장 많이 사용된 캐릭터 TOP 3")
            # TOP 3 자리표시자
            if character_pickrates and len(character_pickrates) >= 3:
                top1, top2, top3 = st.columns(3)
                cols = [top1, top2, top3]
                
                # 1위부터 3위까지 반복문 돌면서 데이터 매칭
                for i, row in enumerate(character_pickrates[:3]):
                    with cols[i]:
                        # 캐릭터 초상화 (나중에 실제 캐릭터 이미지 URL 구조로 교체하세요!)
                        st.markdown(f'<img src="{CHAR_IMG.get(row['char_name'])}" style="width: 60px; border-radius: 10px; margin-bottom: 8px; display: block; margin: 0 auto;">', unsafe_allow_html=True)
                        
                        # 줄바꿈 없이 깔끔하게 한 줄로 이름, 픽률, 의지까지 출력
                        stat_html = f"""
                        <div style="text-align: center; line-height: 1.5; margin-top: 8px;">
                            <span style="font-size: 16px; font-weight: bold;">{row['rank']}위: {row['char_name']}</span><br>
                            <span style="color: #eab308; font-weight: 500; font-size: 14px;">📊 {row['pick_rate']}%</span><br>
                            <img src = '{WEAPON_IMG.get(row['best_weapon'])}' width='60'>
                        </div>
                        """
                        st.markdown(stat_html, unsafe_allow_html=True)
            
            # 💡 아직 자정이 안 지났거나 데이터가 부족해서 테이블이 비어있을 때
            else:
                st.info("⏳ 현재 충분한 랭킹 데이터가 쌓이지 않아 통계를 산출 중입니다. (매일 자정 갱신)")

    st.write("") # 간격 띄우기

    # ==========================================
    # 2. 추천 덱 2개 (가로 2칸 분할)
    # ==========================================
    st.subheader("📋 추천 덱")
    rec1, rec2 = st.columns(2)
    
    with rec1:
        with st.container(border=True):
            st.markdown("#### 🔹 1,000만 점의 정석")
            st.caption("가장 안정적인 국민 조합")

            stable_info = recommended_decks.get("stable_deck", {})
            stable_chars = stable_info.get("chars")
            stable_weapons = stable_info.get("weapons")
            
            if stable_chars and stable_weapons:
                c1, c2, c3, c4 = st.columns(4)
                
                # zip을 써서 캐릭터와 의지를 한 번에 묶어서 출력합니다.
                cols = [c1, c2, c3, c4]
                for i, (char, weapon) in enumerate(zip(stable_chars, stable_weapons)):
                    with cols[i]:
                        st.image(CHAR_IMG.get(char, "https://via.placeholder.com/80"))
                        st.caption(f"<div style='text-align: center; white-space: nowrap; font-size:14px; margin-bottom: 5px;'>{char}</div>", unsafe_allow_html=True)
                        st.markdown(f"<img src='{WEAPON_IMG.get(weapon, 'https://via.placeholder.com/60')}' width='60'>", unsafe_allow_html=True)
    with rec2:
        with st.container(border=True):
            st.markdown("#### 🔹 3,000만 점 고점 돌파")
            st.caption("랭커들을 위한 극한의 조합")
            # 덱 이미지 4개
            high_info = recommended_decks.get("high_score_deck", {})
            high_chars = high_info.get("chars")
            high_weapons = high_info.get("weapons")
            
            if high_chars and high_weapons:
                c1, c2, c3, c4 = st.columns(4)
                
                cols = [c1, c2, c3, c4]
                for i, (char, weapon) in enumerate(zip(high_chars, high_weapons)):
                    with cols[i]:
                        st.image(CHAR_IMG.get(char, "https://via.placeholder.com/80"))
                        st.caption(f"<div style='text-align: center; white-space: nowrap; font-size:14px; margin-bottom: 5px;'>{char}</div>", unsafe_allow_html=True)
                        st.markdown(f"<img src='{WEAPON_IMG.get(weapon, 'https://via.placeholder.com/60')}' width='60'>", unsafe_allow_html=True)
    st.write("")

    # ==========================================
    # 3. 명예의 전당 4개 (2x2 그리드 배열)
    # ==========================================
    st.subheader("🏆 명예의 전당")
    st.write("---")
    bg_url=BOSS_BG_URLS.get(boss_name, "https://via.placeholder.com/300x300?text=Boss+Image")

    def hof_UI(title):
        if title in hof_data:
            item=hof_data[title]
            draw_ranking_card(item=item, bg_url=bg_url)
            colu1, colu2 = st.columns([3, 1])
            with colu2:
                if st.button("상세 보기", key=f"btn_{boss_name}_{title}", width='stretch'):
                    item_best_overall = call_records(item["id"])
                    go_to_detail_page(item_best_overall, "pages/boss.py", boss_name)
        else:
            st.info("데이터 집계 중입니다.")

    st.subheader("🥇 세계 최강자")
    hof_UI("best_overall")  
    
    st.subheader("🥈 2형까진 무과금임")
    hof_UI("under_2_portray")

    st.subheader("🥉 명함단은 승리한다")
    hof_UI("no_portray")

    st.subheader("👍 너넨 싹 다 개추다")
    hof_UI("respect")