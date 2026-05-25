import streamlit as st 
from PIL import Image
import io
import hashlib
import time

def load_css(file_path):
    with open(file_path, encoding='utf-8') as f:
        st.markdown(
            f"<style>{f.read()}</style>", 
            unsafe_allow_html=True)
        
@st.cache_data
def get_css_text(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return f"<style>{f.read()}</style>"

def compress_image(uploaded_file):
    if uploaded_file is not None:
        uploaded_file.seek(0)
    # 1. 유저가 올린 사진을 엽니다.
    img = Image.open(uploaded_file)
    
    # 만약 사진이 RGBA(투명도 있음)인데 JPEG로 저장하려 하면 에러가 날 수 있으니,
    # 우리는 무조건 투명도를 지원하는 WebP로 바꿀 겁니다.
    
    # 2. 가로 길이가 1280px을 넘으면 비율에 맞춰서 줄여줍니다. (용량 폭풍 감소)
    max_width = 1280
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
    # 3. WebP 형식으로 압축해서 메모리(바구니)에 임시로 담습니다.
    img_byte_arr = io.BytesIO()
    # quality=80 이면 눈으로 볼 때 화질 저하는 없으면서 용량은 원본의 1/5 수준으로 박살납니다!
    img.save(img_byte_arr, format='WEBP', quality=80) 
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()


def assign_global_ranks(data):
    """
    순수하게 데이터를 점수순으로 정렬하고 전체 등수(global_rank)만 매겨서 돌려줍니다.
    (💡 나중에 통계/분석 페이지를 만들 때 이 함수만 쏙 빼가서 쓰시면 됩니다!)
    """
    sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
    
    for i, item in enumerate(sorted_data):
        if i > 0 and item.get("score") == sorted_data[i-1].get("score"):
            item["global_rank"] = sorted_data[i-1]["global_rank"]
        else:
            item["global_rank"] = i + 1
            
    return sorted_data

def filter_records(data, search_char=None, search_nickname=None):
    """
    넘겨받은 데이터에서 유저가 검색한 조건만 뜰채로 걸러냅니다.
    """
    filtered = data
    if search_char:
        filtered = [item for item in filtered if search_char in item.get("characters", [])]
        
    if search_nickname: 
        filtered = [item for item in filtered if search_nickname in item.get("nickname", "")]
        
    return filtered

def filter_boss_page(boss_number):
    boss_mapping = {
        "1": "괴멸의 궤도",
        "2": "급성 선홍증",
        "3": "신앙의 이동"
    }
    st.session_state["current_link_boss"] = boss_mapping.get(boss_number, None)
    return 

def to_analyze_recommended_decks(chars, portrays):

    deck_key = ",".join(sorted(chars))

    total_portrays = sum(portrays)
    return deck_key, total_portrays



def generate_deck_code(chars, weapons, portrays, resonances, mods):
    """
    덱 구성 요소와 현재 시간을 조합해 8자리의 고유 덱 코드를 생성합니다.
    """
    # 1. 모든 리스트 요소와 시간을 하나의 긴 문자열로 이어 붙입니다.
    raw_string = f"{chars}_{weapons}_{portrays}_{resonances}_{mods}_{time.time()}"
    
    # 2. SHA-256 방식으로 해싱합니다.
    hashed_obj = hashlib.sha256(raw_string.encode('utf-8'))
    
    # 3. 해시 결과(16진수)에서 앞 8자리만 잘라내고, 대문자로 바꿔서 폼나게 만듭니다.
    # 예: "a1b2c3d4..." -> "A1B2C3D4"
    deck_code = hashed_obj.hexdigest()[:8].upper()
    
    return deck_code