import streamlit as st
import os
import uuid
from supabase import create_client, Client
from services.utils import compress_image

url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

@st.cache_data(ttl=3600)
def load_game_assets():
    # 1. 캐릭터 표 읽어오기
    char_res = supabase.table("characters").select("*").execute()
    char_dict = {item["name"]: item["image_url"] for item in char_res.data}

    char_blocks = {item["name"]: item.get("resonance_block", "") for item in char_res.data}
    
    # 2. 의지 표 읽어오기
    weapon_res = supabase.table("weapons").select("*").execute()
    weapon_dict = {item["name"]: item["image_url"] for item in weapon_res.data}

    # 💡 [추가] 공명 패턴 표 읽어오기
    pattern_res = supabase.table("resonance_pattern").select("*").execute()
    # shape_code(기호)를 키로 삼고, 이름과 이미지 URL을 저장합니다.
    pattern_dict = {}
    for item in pattern_res.data:
        code = item["resonance_block"].strip()
        if code not in pattern_dict:
            pattern_dict[code] = [] # 방이 없으면 새로 만듦
        
        # 덮어씌워지지 않게 방(리스트) 안에 밀어넣기(append)
        pattern_dict[code].append({
            "name": item["block_pattern"],
            "url": item["pattern_URL"]
        })
        # 기존 코드 아래에 추가
        # 캐릭터별 추천 변조를 담은 딕셔너리 (값이 없으면 "게시하지 않음"을 기본으로 줍니다)
        char_rec_mods = {
            item["name"]: item.get("recommended_mod") or "게시하지 않음" 
            for item in char_res.data
        }
    
    # 리턴값에 char_rec_mods를 추가해 줍니다.
    return char_dict, weapon_dict, char_blocks, pattern_dict, char_rec_mods

CHAR_IMG, WEAPON_IMG, CHAR_BLOCKS, PATTERN_DICT, CHAR_REC_MODS = load_game_assets()

def load_board_data():
    response = supabase.table("raid_records").select("*").eq("status", 1).execute()
    
    raw_list = response.data
    
    grouped_dict = {}
    for record in raw_list:
        # 💡 드디어 찾은 진짜 이름표 적용!
        boss_name = record["boss_name"] 
        if boss_name not in grouped_dict:
            grouped_dict[boss_name] = []
        grouped_dict[boss_name].append(record)
        
    return grouped_dict

def find_deck_in_DB(target_code):
    response = supabase.table("raid_records").select("*").eq("deck_code", target_code).limit(1).execute()

    if response.data:
        record = response.data[0]
        st.session_state["selected_record"] = record
        st.switch_page("pages/detail.py")

    else:
        st.query_params.clear()
        st.switch_page("pages/error.py")

def delete_storage_image(image_url):
    """URL을 받아서 스토리지에서 조용히 삭제해주는 함수"""
    if not image_url or "http" not in image_url:
        return
    try:
        pure_filename = image_url.split("/")[-1].split("?")[0].strip()
        #st.write(f"지우려는 파일명: {pure_filename}")

        supabase.storage.from_("raid_proofs").remove([pure_filename])
        #st.write("삭제 결과:", response)
    except:
        pass

def upload_storage_image(image_file, bucket_name="raid_proofs"):
    """
    이미지 파일을 받아 Supabase에 업로드하고, 공개 URL을 반환하는 함수
    """
    if image_file is None:
        return ""
        
    try:
        # 1. 겹치지 않는 고유한 파일명 생성
        file_name = f"{uuid.uuid4().hex}.webp"
        
        # 2. 업로드 진행 (기존에 쓰시던 압축 함수 적용)
        supabase.storage.from_(bucket_name).upload(
            file_name, 
            compress_image(image_file), 
            {"content-type": "image/webp"}
        )
        
        # 3. 성공적으로 올라갔다면 URL 반환
        return supabase.storage.from_(bucket_name).get_public_url(file_name)
        
    except:
        return ""
    
def edit_storage_image(old_url, new_image_file):
    """
    기존 이미지 URL과 새로운 이미지 파일을 받아서, 스토리지에서 기존 이미지를 삭제하고 새 이미지를 업로드한 후 새 URL을 반환하는 함수
    """
    delete_storage_image(old_url)
    return upload_storage_image(new_image_file)
    
def search_my_records(nickname):
    response = supabase.table("raid_records").select("*").eq("nickname", nickname).execute()
    return response.data

def submit_result_of_my_record(status, mode, data, record_id=None):
    if status:
        try:
            if mode == "register":
                supabase.table("raid_records").insert(data).execute()
                st.success("🎉 기록 등록 완료!")
                st.session_state.pop("random_nickname", None)
                if "preset_data" in st.session_state:
                    del st.session_state["preset_data"]
            else:
                supabase.table("raid_records").update(data).eq("id", record_id).execute()
                st.success("🎉 수정이 완료되었습니다!")
            import time
            time.sleep(1.5)
            
            deck_code=data.get("deck_code")
            find_deck_in_DB(deck_code)

        except Exception as e:
            st.error(f"DB 등록 중 오류가 발생했습니다.{e}")
    else:
        st.error(data)


def get_recommended_decks(boss_name):
    recommended_data = {"stable_deck": None, "high_score_deck": None}
    try:
        # 아까 만든 SQL 함수 호출! 인자로 보스 이름을 넘겨줍니다.
        res = supabase.rpc("get_recommended_decks", {"p_boss_name": boss_name}).execute()
        if res.data:
            recommended_data = res.data
    except Exception as e:
        st.error(f"덱 정보를 불러오지 못했습니다.{e}")
    return recommended_data

def get_recommended_decks_preset(boss_name, deck_type="stable"):
    response=get_recommended_decks(boss_name)
    if deck_type == "stable":
        deck_info = response.get("stable_deck") or {}
    elif deck_type == "high":
        deck_info = response.get("high_score_deck") or {}
    else:
        return {}

    # 3. 박스 안에 캐릭터와 의지 배열이 잘 들어있는지 확인합니다.
    chars = deck_info.get("chars")
    weapons = deck_info.get("weapons")

    # 4. 데이터가 존재한다면, 프론트엔드가 요구하는 형식의 딕셔너리로 묶어서 던져줍니다!
    if chars and weapons:
        return {
            "boss": boss_name,
            "chars": chars,
            "weapons": weapons
        }
    else:
        # 해당 보스/점수대의 기록이 아직 없으면 빈칸 리턴
        return {}

def get_character_pickrate(boss_name):
    try:
        response = supabase.table("boss_character_stats") \
            .select("rank, char_name, pick_rate, best_weapon") \
            .eq("boss_name", boss_name) \
            .order("rank") \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"캐릭터 픽률 정보를 불러오지 못했습니다.{e}")
        return []

@st.cache_data(ttl=3600)    
def get_hall_of_fame_data(boss_name):
    """
    명예의 전당 ID를 이용해 원본 기록의 닉네임, 점수, 덱 정보를 한 번에 가져옵니다.
    """
    try:
        # 💡 핵심: select 안에 괄호를 쓰면 두 테이블이 마법처럼 조인됩니다!
        response = supabase.table("hall_of_fame") \
            .select("title, record_id, raid_records(nickname, score, characters)") \
            .eq("boss_name", boss_name) \
            .execute()
            
        # 가져온 데이터를 화면에서 쓰기 좋게 딕셔너리로 조립합니다.
        hof_dict = {}
        for row in response.data:
            title = row["title"] 
            record_id= row["record_id"]               # 예: 'best_overall'
            record = row["raid_records"]        # 조인된 원본 데이터 덩어리
            
            # 카드를 그리는 함수가 요구하는 포맷으로 딱 맞춰줍니다.
            if record:
                hof_dict[title] = {
                    "id": record_id,
                    "nickname": record["nickname"],
                    "score": record["score"],
                    "characters": record["characters"]
                }
                
        return hof_dict
        
    except Exception as e:
        st.error(f"명예의 전당 데이터를 불러오지 못했습니다.")
        return {}
    
def call_records(record_id):
    """
    유저가 '상세 보기' 등을 눌러 신호를 주었을 때만 
    해당 ID의 원본 기록을 DB에서 딱 한 줄 가져옵니다.
    """
    try:
        response = supabase.table("raid_records") \
            .select("nickname, score, characters, weapons, portrays, resonances, comment, proof_url, video_url, status") \
            .eq("id", record_id) \
            .single() \
            .execute()
            
        return response.data # {nickname: '...', score: ...} 형태의 딕셔너리 반환
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None
    


def code_to_deck(input_deck_val):
    if input_deck_val:
        # --- [스마트 파싱 로직] ---
        # 1. 링크 통째로 넣었을 경우를 대비해 'deck=' 뒤의 코드만 추출
        if "deck=" in input_deck_val:
            # 'deck=' 기준으로 자르고, 혹시 뒤에 다른 인자(&)가 있으면 더 자름
            target_code = input_deck_val.split("deck=")[-1].split("&")[0].strip().upper()
        else:
            # 그냥 코드만 넣었을 경우 대문자로 변환
            target_code = input_deck_val.upper()
        
        # 2. DB에서 해당 덱 코드 검색
        deck_res = supabase.table("raid_records").select("*").eq("deck_code", target_code).limit(1).execute()
        
        if deck_res.data:
            pulled = deck_res.data[0]
            
            # 3. 찾은 데이터를 세션 스테이트(각 슬롯의 Key)에 강제 주입
            for i in range(4):
                # 캐릭터, 의지, 형상
                st.session_state[f"char_{i}"] = pulled["characters"][i] if i < len(pulled["characters"]) else "🔎검색..."
                st.session_state[f"weap_{i}"] = pulled["weapons"][i] if i < len(pulled["weapons"]) else "🔎검색..."
                st.session_state[f"port_{i}"] = pulled["portrays"][i] if i < len(pulled["portrays"]) else 0
                
                # 공명 레벨 (슬라이더 & 입력칸)
                res_val = pulled.get("resonances", [0,0,0,0])[i]
                st.session_state[f"res_slider_reg_{i}"] = res_val
                st.session_state[f"res_input_reg_{i}"] = res_val
                
                # 공명 변조
                mod_val = pulled.get("resonances_mods", ["게시하지 않음"]*4)[i]
                st.session_state[f"mod_{i}"] = mod_val
            
            st.toast(f"✅ 덱({target_code}) 정보를 성공적으로 불러왔습니다!", icon="🎯")
        else:
            st.error("🚨 존재하지 않는 덱 코드입니다. 주소를 다시 확인해 주세요.")
    else:
        st.warning("⚠️ 코드를 먼저 입력해 주세요!")

