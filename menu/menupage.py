import streamlit as st
from services.config import BOSS_BG_URLS, CURRENT_SEASON_BOSSES

def menu_page_display():
    
    
    if "show_guide_img" not in st.session_state:
        st.session_state["show_guide_img"] = False

    # 2. 버튼 배치 (가운데 정렬을 원하시면 컬럼을 쪼개서 넣으세요)
    btn_col1, btn_col2 = st.columns([8, 2])
    with btn_col1:
        st.title("리버스: 1999 레이드 기록소")
        st.subheader("3.5버전 <터과이즈 뱀 클럽> 갈기의 게시판 진행 상황")

    with btn_col2:
        if st.button("💡 이용 가이드", width='stretch'):
            # 버튼을 누를 때마다 사진 보이기 상태를 반전(Toggle)시킵니다.
            st.session_state["show_guide_img"] = not st.session_state["show_guide_img"]

    # 3. 상태가 True일 때만 이미지를 표시합니다.
    if st.session_state["show_guide_img"]:
        # 💡 여기에 방금 캡처하신 도움말 이미지의 URL을 넣으세요!
        # 로컬 파일이라면 st.image("path/to/your/image.png") 도 가능합니다.
        guide_img_url = "help_main.png" 
        
        st.image(guide_img_url, caption="레이드 기록소 이용 가이드 (다시 버튼을 누르면 닫힙니다)", width='stretch')
        st.write("---")
    st.write("---") 

    # 1. 화면을 3개의 열(Column)로 나눕니다.
    # col1, col2, col3이라는 변수에 각각의 공간을 할당합니다.
    # 1. 현재 시즌 보스의 개수만큼 알아서 컬럼을 쪼개줍니다. (3마리면 3등분, 4마리면 4등분!)
    cols = st.columns(len(CURRENT_SEASON_BOSSES))

    # 2. 리스트를 돌면서 순서대로(i) 보스 이름(boss_name)을 꺼내서 카드를 그립니다.
    for i, boss_name in enumerate(CURRENT_SEASON_BOSSES):
        with cols[i]:
            st.markdown(f"<h3 style='text-align: center;'>{boss_name}</h3>", unsafe_allow_html=True)
            
            # 💡 i는 0부터 시작하므로, 주소창에 넘길 boss 번호는 i + 1 로 맞춰줍니다. (1, 2, 3...)
            img_html = f"""
                <a href="/?boss={i + 1}" target="_self">
                    <img src="{BOSS_BG_URLS[boss_name]}" style="width: 100%; border-radius: 10px; margin-bottom: 10px;">
                </a>
            """
            st.markdown(img_html, unsafe_allow_html=True)

    st.write("---")

