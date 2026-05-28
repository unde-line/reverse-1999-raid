import streamlit as st
from services.DB import submit_result_of_my_record
from editrecord.editUI import draw_record_form
from editrecord.editsystem import process_record_payload
import random

@st.dialog("✨ 새로운 레이드 기록 등록", width="large")
def show_register_popup():
    

    st.write("리버스: 1999 레이드 기록을 등록해 주세요. (관리자 승인 후 반영됩니다)")
    if "random_nickname" not in st.session_state:
        st.session_state["random_nickname"] = f"버틴-{random.randint(1000, 9999)}"

    submit_btn, raw_data, images = draw_record_form(mode="insert")
    
    if submit_btn:
        with st.spinner("서버로 데이터를 전송 중입니다..."):
            is_success, result = process_record_payload("insert", raw_data, images)

            submit_result_of_my_record(is_success, "register", result)

                