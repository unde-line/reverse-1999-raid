import streamlit as st

def error_page_display():
    st.title("오류 페이지")
    st.write("죄송합니다. 요청하신 페이지를 찾을 수 없습니다.")
    if st.button("메인 화면으로 돌아가기", icon="🏠"):
        st.query_params.clear()
        st.switch_page("pages/menu.py")  # 랭킹 페이지로 돌아가기

error_page_display()