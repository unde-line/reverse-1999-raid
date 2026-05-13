import streamlit as st
from services.DB import supabase


@st.dialog("🗑️ 기록 삭제")
def show_delete_popup(record): # 💡 id 대신 record(데이터 보따리) 전체를 받습니다!
    st.warning("정말 이 기록을 삭제하시겠습니까? (복구할 수 없습니다)")
    pwd_input = st.text_input("🔒 글 작성 시 입력한 비밀번호", type="password", max_chars=20)
    
    if st.button("🚨 영구 삭제하기", type="primary", width='stretch'):
        if pwd_input == record["password"]:
            with st.spinner("데이터와 사진을 깔끔하게 지우는 중입니다..."):
                try:
                    # 🧹 1. 창고(Storage)에서 사진 파일부터 삭제!
                    # 전체 URL에서 맨 마지막 슬래시(/) 뒤의 파일명만 가져오고, 혹시 모를 물음표(?) 뒤의 찌꺼기도 잘라냅니다.
                    pure_proof = record["proof_url"].split("/")[-1].split("?")[0]
                    pure_portray = record["portray_proof_url"].split("/")[-1].split("?")[0]
                    
                    # 도메인 다 떼고 순수 파일명(예: a1b2c.webp)만 넘겨서 완벽하게 삭제!
                    supabase.storage.from_("raid_proofs").remove([pure_proof, pure_portray])
                    
                    # 🧹 2. 창고를 비웠으니, 이제 DB에서 기록을 삭제!
                    supabase.table("raid_records").delete().eq("id", record["id"]).execute()
                    
                    st.success("기록과 사진이 찌꺼기 없이 깔끔하게 삭제되었습니다!")
                    import time
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"삭제 중 오류가 발생했습니다: {e}")
        else:
            st.error("비밀번호가 일치하지 않습니다.")