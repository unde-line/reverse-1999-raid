import streamlit as st 
from PIL import Image
from collections import Counter
import io

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
    if uploaded_file is None:
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

# 1. 🏆 캐릭터 픽률 순위 정렬 함수
def sort_by_character_usage(records):
    """
    모든 기록을 뒤져서 '가장 많이 사용된 캐릭터' 순서대로 정렬해 돌려줍니다.
    출력 예시: [('투스페어리', 150), ('곡랑', 120), ('갈기 모래', 85), ...]
    """
    all_chars = []
    for r in records:
        all_chars.extend(r.get("characters", [])) # 빈 리스트 방어
        
    # Counter가 개수를 세고, most_common()이 알아서 1등부터 꼴등까지 정렬해줍니다!
    return Counter(all_chars).most_common()


# 2. ⚔️ 의지 사용률 순위 정렬 함수 (캐릭터와 원리 동일)
def sort_by_weapon_usage(records):
    """
    '가장 많이 사용된 의지' 순서대로 정렬합니다.
    출력 예시: [('오락 지상주의', 200), ('두 번째 생명', 90), ...]
    """
    all_weapons = []
    for r in records:
        all_weapons.extend(r.get("weapons", []))
        
    return Counter(all_weapons).most_common()


# 3. 👥 가장 많이 사용된 덱(조합) 정렬 함수 (이게 진짜 꿀기능입니다!)
def sort_by_deck_usage(records):
    """
    '어떤 4인 조합이 가장 많이 쓰였나?'를 찾아 정렬합니다.
    출력 예시: [(('갈기 모래', '곡랑', '이졸데', '투스페어리'), 45), ...]
    """
    decks = []
    for r in records:
        chars = r.get("characters", [])
        if len(chars) > 0:
            # 💡 핵심: 픽 순서가 달라도 같은 덱으로 취급하기 위해 정렬(sorted) 후 튜플로 묶어줍니다.
            deck_combo = tuple(sorted(chars)) 
            decks.append(deck_combo)
            
    return Counter(decks).most_common()

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