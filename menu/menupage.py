import streamlit as st
from services.config import BOSS_BG_URLS

def menu_page_display():
    st.title("리버스: 1999 레이드 기록소")
    st.subheader("3.4버전 불로춘 갈기의 게시판 진행 상황")

    st.write("---") 

    # 1. 화면을 3개의 열(Column)로 나눕니다.
    # col1, col2, col3이라는 변수에 각각의 공간을 할당합니다.
    col1, col2, col3 = st.columns(3)

    # 2. 첫 번째 열 (왼쪽)
    with col1:
        st.header("괴멸의 궤도")
        st.image(BOSS_BG_URLS["괴멸의 궤도"], width='stretch', caption="괴멸의 궤도")

    # 3. 두 번째 열 (가운데)
    with col2:
        st.header("급성 선홍증")
        st.image(BOSS_BG_URLS["급성 선홍증"], width='stretch', caption="급성 선홍증")

    # 4. 세 번째 열 (오른쪽)
    with col3:
        st.header("신앙의 이동")
        st.image(BOSS_BG_URLS["신앙의 이동"], width='stretch', caption="신앙의 이동")

    st.write("---")

