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
    
    # 2. 의지 표 읽어오기
    weapon_res = supabase.table("weapons").select("*").execute()
    weapon_dict = {item["name"]: item["image_url"] for item in weapon_res.data}
    
    return char_dict, weapon_dict

CHAR_IMG, WEAPON_IMG = load_game_assets()

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


def insert_new_record(boss, score, nickname, password, selected_chars, selected_weapons, portrays, resonances, user_comment, youtube_url, proof_url, portray_url):
    insert_data = {
        "boss_name": boss,
        "score": score,
        "nickname": nickname,
        "password": password,
        "characters": selected_chars,       # 리스트 형태 [캐1, 캐2, 캐3, 캐4]
        "weapons": selected_weapons,   # 리스트 형태 [의1, 의2, 의3, 의4]
        "portrays": portrays,          # 리스트 형태 [형1, 형2, 형3, 형4]
        "resonances": resonances,      # 리스트 형태 [공1, 공2, 공3, 공4]
        "proof_url": proof_url,
        "portray_proof_url": portray_url,
        "comment": user_comment,      # 유저 코멘트 추가
        "video_url": youtube_url,   # 유튜브 링크 추가
        "status": 0           # 관리자 승인 전까지는 게시판에 안 보이게 설정
    }
    supabase.table("raid_records").insert(insert_data).execute()

def edit_data(record_id, new_boss, new_score, new_chars, new_weapons, new_portrays, new_resonances, new_comment, new_youtube, new_proof_url, new_portray_url):
    update_data = {
        "boss_name": new_boss,
        "score": new_score,
        "characters": new_chars,
        "weapons": new_weapons,
        "portrays": new_portrays,
        "resonances": new_resonances,
        "comment": new_comment,
        "video_url": new_youtube,
        "proof_url": new_proof_url,
        "portray_proof_url": new_portray_url,
        "status": 0           # 수정된 기록은 다시 관리자의 승인을 받아야 게시판에 보이도록 설정
    }
    supabase.table("raid_records").update(update_data).eq("id", record_id).execute()
    