from boss.bosspage import boss_page_display
import streamlit as st
from services.config import boss_names

current_boss = st.session_state.get("current_link_boss", None)  # 메뉴에서 클릭한 보스 이름 가져오기


# 만약 주소에 boss 이름이 들어있다면? (예: /?boss=괴멸의 궤도)
if current_boss in boss_names:
    boss_page_display(boss_name=current_boss)
else:
    st.switch_page("pages/error.py")  # 유효하지 않은 boss 이름이면 에러 페이지로 이동  