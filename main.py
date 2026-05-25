import streamlit as st


from services.config import CURRENT_SEASON_BOSSES
from services.utils import load_css, filter_boss_page
from services.DB import find_deck_in_DB


st.set_page_config(page_title="리버스:1999 레이드 기록소", page_icon="img/Bossrush_icon_assess_sss7.webp")
st.sidebar.image("img/Bossrush_icon_assess_sss7.webp", width='stretch')
st.sidebar.header("리버스:1999 레이드 기록소")

load_css('main.css')

#TODO: (DB)renewal_page 만들기



# ==========================================
# 세션 상태 초기화
# ==========================================
default_states = {"selected_record": None, "last_search_rank": None, "last_search_edit": None}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value


for boss_name in CURRENT_SEASON_BOSSES:
    if f"page_{boss_name}" not in st.session_state:
        st.session_state[f"page_{boss_name}"] = 1

menu_page = st.Page("pages/menu.py", title="메인 화면", icon="🏠", default=True)
ranking_page = st.Page("pages/rank.py", title="랭킹 게시판", icon="📊")
edit_page = st.Page("pages/toedit.py", title="기록 등록하기", icon="📝")
detail_page = st.Page("pages/detail.py", title="상세 기록 보기")
boss_page = st.Page("pages/boss.py", title="보스 상세 페이지")
error_page = st.Page("pages/error.py", title="오류 페이지", icon="❌")
#TODO: 보스 상세 페이지 만들기


# ==========================================
# 사이드바 설정
# ==========================================

pg = st.navigation([menu_page, ranking_page, edit_page, detail_page, boss_page, error_page], position="hidden")

if "deck" in st.query_params:
    find_deck_in_DB(st.query_params["deck"])


if "boss" in st.query_params:
    boss_number = st.query_params["boss"]
    filter_boss_page(boss_number)
    st.switch_page("pages/boss.py")  # 주소에 boss=이름이 있으면 보스 페이지로 이동

with st.sidebar:
    st.page_link(menu_page, label="메인 화면", icon="🏠")
    st.page_link(ranking_page, label="랭킹 게시판", icon="📊")
    st.page_link(edit_page, label="기록 등록하기", icon="📝")

pg.run()  # 선택된 페이지를 실행합니다!