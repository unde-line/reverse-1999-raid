import streamlit as st
from editrecord.register import show_register_popup
from editrecord.edit import show_edit_popup
from editrecord.delete import show_delete_popup
import services.DB

def edit_page_display():
    # ==========================================
    # 🖥️ 메인 화면 (검색창 & 팝업 호출 버튼)
    # ==========================================
    st.markdown("## 🔍 내 기록 찾기 & 등록")

    # 검색창과 버튼을 나란히 배치하기
    search_col, btn_col = st.columns([3, 1])

    with search_col:
        saved_nickname = st.session_state.get("last_search_edit", "")

        if "search_edit" not in st.session_state and st.session_state.get("last_search_edit"):
            st.session_state["search_edit"] = st.session_state["last_search_edit"]
        search_nickname = st.text_input("👤 작성한 닉네임을 입력해서 내 기록을 찾아보세요!", value=saved_nickname,
                                        placeholder="예: 타임키퍼...", max_chars=10)
        st.session_state["last_search_edit"] = search_nickname  # 검색어를 세션에 저장해서 페이지 이동 후에도 유지되도록 합니다.

    if search_nickname:
        # 2. DB에서 해당 닉네임이 쓴 글만 쏙 골라옵니다.
        my_records = services.DB.search_my_records(search_nickname)

        if len(my_records) == 0:
            st.warning("해당 닉네임으로 등록된 기록이 없습니다.")
        else:
            st.success(f"총 {len(my_records)}개의 기록을 찾았습니다!")
            
            # 3. 찾은 기록들을 반복문으로 하나씩 보여주며 옆에 버튼을 달아줍니다.
            for record in my_records:
                # 예쁘게 박스(컨테이너) 안에 담아서 보여줍니다.
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**[{record['boss_name']}]** 점수: {record['score']:,}점")
                        if record['status'] == 2:
                            st.caption(f"반려됨 (사유: {record['deny_reason']})")
                        elif record['status'] == 1:
                            st.caption(f"(승인)등록일: {record['created_at'][:10]}")
                        elif record['status'] == 0:
                            st.caption(f"(대기 중...)등록일: {record['created_at'][:10]}")
                        else:
                            st.caption("오류 발생. 관리자 문의 요망.")
                        
                    
                    with col2:
                        # 💡 버튼의 key 값에 고유한 record['id']를 줘서 버튼끼리 안 겹치게 합니다!
                        if st.button("상세", key=f"detail_{record['id']}", width='stretch'):
                            st.session_state["selected_record"] = record  # 세션 가방에 기록 전체를 넣어줍니다!
                            st.session_state.previous_page = "pages/toedit.py"  # 이전 페이지 정보도 저장
                            st.switch_page("pages/detail.py")  # 상세 페이지로 이동!
                    
                    with col3:
                        # 💡 버튼의 key 값에 고유한 record['id']를 줘서 버튼끼리 안 겹치게 합니다!
                        if st.button("✏️ 수정", key=f"edit_{record['id']}", width='stretch'):
                            show_edit_popup(record) # 수정 팝업창 호출!
                            
                    with col4:
                        if st.button("🗑️ 삭제", key=f"del_{record['id']}", type="primary", width='stretch'):
                            show_delete_popup(record) # 👈 record 전체를 넘겨주도록 수정!
    with btn_col:
        # 이 버튼을 누르면 위에서 만든 팝업 함수가 실행됩니다!
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ 새 기록 등록", width='stretch', type="primary"):
            show_register_popup()

