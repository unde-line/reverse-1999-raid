import streamlit as st
from services.DB import submit_result_of_my_record
from editrecord.editUI import draw_record_form
from editrecord.editsystem import get_record_data, process_record_payload



@st.dialog("✏️ 기록 전면 수정", width="large")
def show_edit_popup(record):

    get_record_data(record)

    st.warning(f"[{record['boss_name']}] 기록의 모든 내용을 수정합니다.")

    default_data = {
        "boss": record.get("boss_name"),
        "score": int(record.get("score", 0)),
        "nickname": record.get("nickname"),
        "comment": record.get("comment"),
        "youtube": record.get("video_url")
    }
    
    submit_btn, raw_data, images = draw_record_form(mode="edit", default_data=default_data, record_id=record["id"])
    
    if submit_btn:
        with st.spinner("수정된 데이터를 덮어씌우는 중입니다..."):
            is_success, result = process_record_payload("edit", raw_data, images, record=record)
            submit_result_of_my_record(is_success, "edit", result, record_id=record["id"])