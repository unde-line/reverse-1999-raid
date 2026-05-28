import streamlit as st
from services.DB import get_recommended_decks_preset, upload_storage_image, edit_storage_image, CHAR_REC_MODS
from services.utils import to_analyze_recommended_decks, generate_deck_code

def apply_preset_action(boss_name, deck_type):
    preset = get_recommended_decks_preset(boss_name, deck_type)
    
    if preset:
        chars = preset.get("chars", [])
        weapons = preset.get("weapons", [])
        
        # 💡 핵심: 위젯의 key(char_0, weap_0 등)에 데이터를 다이렉트로 덮어씌웁니다!
        for i in range(4):
            char_name = "🔎검색..." # 기본값 세팅
            # 캐릭터 주입
            if len(chars) > i:
                char_name = chars[i]
                st.session_state[f"char_{i}"] = char_name
            # 의지 주입
            if len(weapons) > i:
                st.session_state[f"weap_{i}"] = weapons[i]
            
            # 공명 레벨 주입 (정석은 10, 고점은 13)
            res_level = 10 if deck_type == "stable" else 13
            st.session_state[f"res_slider_reg_{i}"] = res_level
            st.session_state[f"res_input_reg_{i}"] = res_level
            # ==========================================================
            # 💡 4. [추가] 공명 변조 주입 (캐릭터 DB 연동)
            # ==========================================================
            if char_name != "🔎검색...":
                # CHAR_REC_MODS 딕셔너리에서 해당 캐릭터의 추천 변조를 가져옵니다. (없으면 기본값)
                recommended_mod = CHAR_REC_MODS.get(char_name, "게시하지 않음")
                st.session_state[f"mod_{i}"] = recommended_mod
            else:
                st.session_state[f"mod_{i}"] = "게시하지 않음"
            # ==========================================================

        # 초기화 버튼 표시를 위해 세션에 남겨둠
        st.session_state["preset_data"] = preset
    else:
        st.toast(f"아직 [{boss_name}]의 덱 데이터가 없습니다!", icon="🚨")

def clear_all_inputs_action(original_record=None):
    if "preset_data" in st.session_state:
        del st.session_state["preset_data"]
        
    for i in range(4):
        if original_record:
            # 💡 [수정 모드] 원래 DB에 있던 기록으로 복구!
            st.session_state[f"char_{i}"] = original_record["characters"][i] if i < len(original_record["characters"]) else "🔎검색..."
            st.session_state[f"weap_{i}"] = original_record["weapons"][i] if i < len(original_record["weapons"]) else "🔎검색..."
            st.session_state[f"port_{i}"] = original_record["portrays"][i] if i < len(original_record["portrays"]) else 0
            
            initial_res = original_record.get("resonances", [0,0,0,0])[i] if i < len(original_record.get("resonances", [])) else 0
            st.session_state[f"res_slider_reg_{i}"] = initial_res
            st.session_state[f"res_input_reg_{i}"] = initial_res
            # ==========================================================
            # 💡 [추가] 공명 변조 원본 복구
            # ==========================================================
            mods_list = original_record.get("resonances_mods", ["게시하지 않음"] * 4)
            st.session_state[f"mod_{i}"] = mods_list[i] if i < len(mods_list) else "게시하지 않음"
        else:
            # 💡 [등록 모드] 완전 빈칸으로 초기화!
            st.session_state[f"char_{i}"] = "🔎검색..."
            st.session_state[f"weap_{i}"] = "🔎검색..."
            st.session_state[f"port_{i}"] = 0
            st.session_state[f"res_slider_reg_{i}"] = 0
            st.session_state[f"res_input_reg_{i}"] = 0
            # ==========================================================
            # 💡 [추가] 공명 변조 빈칸 초기화
            # ==========================================================
            st.session_state[f"mod_{i}"] = "게시하지 않음"
        if original_record:
            st.session_state["edit_boss"] = original_record["boss_name"]
            st.session_state["edit_score"] = int(original_record["score"])

def confirm_preset_callback(boss_name, deck_type):
    # '예'를 눌렀을 때 엔진을 가동하고, 대기 상태를 해제합니다.
    apply_preset_action(boss_name, deck_type)
    if "pending_preset" in st.session_state:
        del st.session_state["pending_preset"]

def cancel_preset_callback():
    # '아니요'를 눌렀을 때 대기 상태만 없앱니다.
    if "pending_preset" in st.session_state:
        del st.session_state["pending_preset"]

def cancel_clear_callback():
    # '아니요'를 누르면 복구하지 않고 경고창만 닫기
    if "pending_clear" in st.session_state:
        del st.session_state["pending_clear"]

def confirm_clear_callback(original_record=None):
    # original_record를 받아서 엔진으로 넘겨줍니다.
    clear_all_inputs_action(original_record)
    if "pending_clear" in st.session_state:
        del st.session_state["pending_clear"]

def process_record_payload(mode, raw_data, images, record=None):
    """
    모든 검증, 이미지 업로드, 덱 코드 생성을 한 번에 처리하고 
    에러가 없으면 (True, DB용 딕셔너리)를 반환합니다.
    """
    # ==========================================
    # 1. 🚨 공통 및 모드별 유효성 검사 (Validation)
    # ==========================================
    if "🔎검색..." in raw_data["chars"] or "🔎검색..." in raw_data["weapons"]:
        return False, "파티원 4명의 캐릭터와 의지를 모두 선택해 주세요!"
    if len(raw_data["password"]) > 20:
        return False, "비밀번호는 최대 20자까지 입력 가능합니다!"

    if mode == "insert":
        if not raw_data["password"] or raw_data["score"] == 0:
            return False, "비밀번호, 점수를 모두 입력해 주세요!"
        if images["proof"] is None or images["portray"] is None:
            return False, "인증 사진 2장을 모두 첨부해 주세요!"
    elif mode == "edit":
        if raw_data["password"] != record["password"]:
            return False, "비밀번호가 일치하지 않습니다!"

    # ==========================================
    # 2. 📸 이미지 업로드 및 URL 획득
    # ==========================================
    try:
        if mode == "insert":
            proof_url = upload_storage_image(images["proof"])
            portray_url = upload_storage_image(images["portray"])
        else: # edit 모드
            proof_url = edit_storage_image(record.get("proof_url", ""), images["proof"]) if images["proof"] else record.get("proof_url", "")
            portray_url = edit_storage_image(record.get("portray_proof_url", ""), images["portray"]) if images["portray"] else record.get("portray_proof_url", "")

        # ==========================================
        # 3. 🧩 덱 키 및 코드 생성
        # ==========================================
        deck_key, total_portrays = to_analyze_recommended_decks(raw_data["chars"], raw_data["portrays"])
        deck_code = generate_deck_code(raw_data["chars"], raw_data["weapons"], raw_data["portrays"], raw_data["resonances"], raw_data["mods"])

        # ==========================================
        # 4. 🎁 최종 딕셔너리 조립 (DB에 바로 쏠 데이터)
        # ==========================================
        final_dict = {
            "boss_name": raw_data["boss"],
            "score": raw_data["score"],
            "characters": raw_data["chars"],
            "weapons": raw_data["weapons"],
            "portrays": raw_data["portrays"],
            "resonances": raw_data["resonances"],
            "comment": raw_data["comment"],
            "video_url": raw_data["youtube"],
            "proof_url": proof_url,
            "portray_proof_url": portray_url,
            "status": 0,
            "deck_key": deck_key,
            "total_portrays": total_portrays,
            "resonances_mods": raw_data["mods"],
            "deck_code": deck_code
        }

        # insert일 때만 닉네임과 비번 추가
        if mode == "insert":
            final_dict["nickname"] = raw_data["nickname"]
            final_dict["password"] = raw_data["password"]

        return True, final_dict

    except Exception as e:
        return False, f"데이터 처리 중 오류 발생: {e}"


def get_record_data(record):
    if st.session_state.get("current_edit_id") != record["id"]:
        st.session_state["current_edit_id"] = record["id"]
        
        # 이전 팝업에서 남았을지 모르는 대기 상태 및 프리셋 데이터 청소
        st.session_state.pop("pending_preset", None)
        st.session_state.pop("pending_clear", None)
        st.session_state.pop("preset_data", None)

        # 💡 [추가] 팝업창이 처음 열릴 때, 보스와 점수의 원본 값을 세션에 미리 심어둡니다!
        st.session_state["edit_boss"] = record["boss_name"]
        st.session_state["edit_score"] = int(record["score"])
        
        # 4명의 기존 캐릭터, 의지, 형상, 공명 정보를 컴포넌트 키 형식에 맞춰 강제 주입
        for i in range(4):
            st.session_state[f"char_{i}"] = record["characters"][i] if i < len(record["characters"]) else "🔎검색..."
            st.session_state[f"weap_{i}"] = record["weapons"][i] if i < len(record["weapons"]) else "🔎검색..."
            st.session_state[f"port_{i}"] = record["portrays"][i] if i < len(record["portrays"]) else 0
            
            initial_res = record["resonances"][i] if i < len(record.get("resonances", [])) else 0
            st.session_state[f"res_slider_reg_{i}"] = initial_res
            st.session_state[f"res_input_reg_{i}"] = initial_res

            # ==========================================================
            # 💡 [추가] 공명 변조 데이터 주입
            # 혹시라도 DB에 배열이 없거나 짧을 경우를 대비해 안전장치(기본값: 게시하지 않음)를 겁니다.
            # ==========================================================
            mods_list = record.get("resonances_mods", [])
            initial_mod = mods_list[i] if i < len(mods_list) else "게시하지 않음"
            st.session_state[f"mod_{i}"] = initial_mod