import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import concurrent.futures
import random
import re
import unicodedata
from urllib.parse import urlparse, unquote
from streamlit_autorefresh import st_autorefresh

# =========================================================
# CẤU HÌNH TỰ ĐỘNG REFRESH (8s)
# =========================================================
st_autorefresh(interval=8000, limit=None, key="f5updater")

TARGET_KEYWORD = "tập gym"

GROUP_URLS = [
    {"name": "Vinmec (Y tế)", "url": "https://www.vinmec.com/vi/tin-tuc/thong-tin-suc-khoe/song-khoe/luu-y-khi-tap-gym-cho-nguoi-moi-bat-dau/"},
    {"name": "California Fitness", "url": "https://cali.vn/blog/kien-thuc-the-hinh/lich-tap-gym-cho-nguoi-moi-bat-dau"},
    {"name": "WheyShop", "url": "https://wheyshop.vn/huong-dan-tap-gym-cho-nguoi-moi-bat-dau.html"},
    {"name": "Thể Hình .com", "url": "https://thehinh.com/lich-tap-gym-cho-nguoi-moi-bat-dau/"},
    {"name": "Elipsport", "url": "https://elipsport.vn/tin-tuc/huong-dan-tap-gym-dung-cach-cho-nguoi-moi-bat-dau_2723.html"},
    {"name": "Swequity (SUF)", "url": "https://swequity.vn/huong-dan-tap-gym-cho-nguoi-moi-bat-dau/"},
    {"name": "CitiGym", "url": "https://citigym.com.vn/tap-gym-la-gi-loi-ich-cua-viec-tap-gym.html"},
    {"name": "Nhà Thuốc Long Châu", "url": "https://nhathuoclongchau.com.vn/bai-viet/tap-gym-la-gi-nhung-loi-ich-tuyet-voi-cua-viec-tap-gym-mang-lai-60472.html"},
    {"name": "Hello Bác Sĩ", "url": "https://hellobacsi.com/the-duc-the-thao/dong-luc-tap-luyen/loi-ich-cua-viec-tap-gym/"},
    {"name": "Toshiko", "url": "https://toshiko.vn/huong-dan-tap-gym-cho-nguoi-moi-bat-dau-hieu-qua-nhat/"},
    {"name": "S-Life Beauty", "url": "https://s-life.vn/tap-gym-cho-nguoi-moi-bat-dau/"},
    {"name": "FitStore", "url": "https://fitstore.vn/lich-tap-gym-cho-nguoi-moi-bat-dau/"},
]

def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).lower()
    return re.sub(r'[-\s]+', '-', text).strip('-')

# --- DANH SÁCH CÂU KHÍCH TƯỚNG ---
def get_trash_talk(winner_name):
    quotes = [
        f"📞 Các group khác phải gọi {winner_name} bằng ĐIỆN THOẠI!",
        f"🎵 {winner_name} thắc mắc các group khác đã nghe bài 'Trình' chưa?",
        f"🤔 Các group khác nặng Vía quá nên mãi ở top dưới hả ta? {winner_name} suy tư.",
        f"✨ Ước gì {winner_name} bớt đẳng cấp một chút để sống hòa đồng thì tốt biết bao!",
        f"👴 'Biết điều tôn trọng người lớn đấy là kính lão đắc thọ', {winner_name} said.",
        f"💸 'Nếu mà các Group khác cảm thấy cuộc sống bế tắc hãy bốc cho mình một bát họ', {winner_name} said.",
        f"🍲 Các nhóm khác thích ăn lẩu thái siêu cay không? {winner_name} sẵn sàng nấu cho nè!",
        f"🚩 Tiến vào lễ đài là {winner_name} và các group còn lại...",
        f"❄️ Ở trên đỉnh lạnh quá, {winner_name} cần tìm người sưởi ấm!",
        f"🔭 {winner_name} đang dùng kính viễn vọng để tìm đối thủ phía sau.",
        f"🚗 Tốc độ này thì {winner_name} bị bắn tốc độ chắc luôn!",
        f"👑 {winner_name}: 'Ngai vàng này hơi cứng nhưng ngồi cũng êm.'",
        f"😂 {winner_name}: 'Ai sợ thì đi về, phong cách, phong cách'",
        f"🚧 Xin lỗi, {winner_name} đang thi công công trình 'Top 1', vui lòng đi lối khác.",
        f"🚀 {winner_name} đã bay ra khỏi trái đất, các bạn ở lại mạnh giỏi.",
        f"📢 Thông báo: {winner_name} đã out trình server!",
        f"👻 Các nhóm khác đâu rồi? {winner_name} thấy cô đơn quá.",
        f"🎓 {winner_name} mở lớp dạy SEO cấp tốc, ai đăng ký không?",
        f"🏆 Cúp này {winner_name} cầm hộ thôi, ai giỏi thì lên lấy lại nhé!"
    ]
    return random.choice(quotes)

def audit_final(group):
    input_url = group['url']
    data = {
        "name": group['name'],
        "score": 100,
        "issues": {"Tech": [], "Pre": [], "Content": []},
        "redirected": False
    }

    AI_TAG = "[ 🤖 AISEO ]"

    try:
        # --- 1. GLOBAL CHECK ---
        start = time.time()
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.get(input_url, headers=headers, timeout=3)
            load_time = time.time() - start
            final_url = res.url
            if final_url.rstrip('/') != input_url.rstrip('/'):
                data['redirected'] = True
        except:
            data['score'] = 0; data['issues']['Tech'].append("💀 Link chết"); return data

        if load_time > 0.5:
            data['score'] -= 10; data['issues']['Tech'].append(f"🐌 Load chậm ({round(load_time,2)}s)")

        parsed = urlparse(final_url)
        path = unquote(parsed.path)
        clean_path = path.strip("/")

        if len(clean_path) > 1:
            if re.search(r'/\d{4}/\d{2}/', path):
                data['score'] -= 15; data['issues']['Tech'].append("🔗 URL chứa ngày tháng")
            if "_" in path:
                data['score'] -= 5; data['issues']['Tech'].append("🔗 URL chứa gạch dưới (_)")
            keyword_slug = slugify(TARGET_KEYWORD)
            if keyword_slug not in path.lower():
                data['score'] -= 10; data['issues']['Tech'].append(f"🔗 URL thiếu từ khóa '{keyword_slug}'")

        soup = BeautifulSoup(res.content, 'html.parser')

        if not soup.find("link", rel=lambda x: x and 'icon' in x.lower()):
            data['score'] -= 2; data['issues']['Tech'].append("🖼️ Thiếu Favicon")

        is_uncat = False
        if soup.find('body', class_=re.compile(r'category-uncategorized')): is_uncat = True
        if soup.find('article', class_=re.compile(r'category-uncategorized')): is_uncat = True
        if is_uncat:
            data['score'] -= 5; data['issues']['Tech'].append("📂 Chưa chọn Chuyên mục")

        # --- 2. PRE-CLICK ---
        title = soup.find('title')
        if title:
            t_text = title.get_text().strip()
            if not t_text.lower().startswith(TARGET_KEYWORD.lower()):
                data['score'] -= 10; data['issues']['Pre'].append("❌ Title: Từ khóa không đứng đầu")
            if not (40 <= len(t_text) <= 70):
                data['score'] -= 5; data['issues']['Pre'].append(f"📏 Title sai độ dài ({len(t_text)})")
        else:
            data['score'] -= 20; data['issues']['Pre'].append("☠️ Mất Title")

        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            m_text = meta.get('content')
            if len(m_text) < 120:
                data['score'] -= 5; data['issues']['Pre'].append("📏 Meta quá ngắn")
            if TARGET_KEYWORD.lower() not in m_text.lower():
                data['score'] -= 5; data['issues']['Pre'].append("🔍 Meta thiếu từ khóa")
        else:
            data['score'] -= 10; data['issues']['Pre'].append("⚠️ Thiếu Meta Description")

        # --- 3. POST-CLICK (CONTENT & AISEO) ---
        h1s = soup.find_all('h1')
        if not h1s:
            data['score'] -= 15; data['issues']['Content'].append(f"{AI_TAG} ⛔ Không tìm thấy thẻ H1")
        else:
            h1_text = h1s[0].get_text().strip().lower()
            if TARGET_KEYWORD.lower() not in h1_text:
                data['score'] -= 10; data['issues']['Content'].append(f"{AI_TAG} ⛔ H1 thiếu từ khóa '{TARGET_KEYWORD}'")

        content_area = (
            soup.find(class_=re.compile(r'entry-content|post-content|wp-block-post-content'))
            or soup.find('article')
            or soup.find('main')
        )

        if content_area:
            text = content_area.get_text(" ", strip=True)
            word_count = len(text.split())

            if word_count < 800:
                data['score'] -= 15; data['issues']['Content'].append(f"{AI_TAG} 📝 Bài quá ngắn ({word_count}/800 từ)")

            first_100_words = " ".join(text.split()[:100]).lower()
            if TARGET_KEYWORD.lower() not in first_100_words:
                data['score'] -= 5; data['issues']['Content'].append(f"{AI_TAG} 📍 Từ khóa không xuất hiện ở mở bài")

            if word_count > 0:
                density = (text.lower().count(TARGET_KEYWORD.lower()) / word_count) * 100
                if density > 3.0:
                    data['score'] -= 20; data['issues']['Content'].append(f"{AI_TAG} ⛔ Spam từ khóa ({round(density,1)}%)")
                elif density < 0.3:
                    data['score'] -= 10; data['issues']['Content'].append("📉 Quá ít từ khóa")

            h2s = content_area.find_all('h2')
            if len(h2s) < 2: data['score'] -= 10; data['issues']['Content'].append(f"{AI_TAG} ⚠️ Thiếu thẻ H2 (Cấu trúc)")

            paragraphs = content_area.find_all('p')
            long_paras = sum(1 for p in paragraphs if len(p.get_text().split()) > 100)
            if long_paras > 0:
                data['score'] -= 5; data['issues']['Content'].append(f"{AI_TAG} 📖 Đoạn văn quá dài (Khó đọc)")

            if not content_area.find_all(['ul', 'ol']):
                data['score'] -= 3; data['issues']['Content'].append(f"{AI_TAG} 📋 Thiếu Danh sách (List)")

            if not content_area.find_all('table'):
                data['score'] -= 5; data['issues']['Content'].append(f"{AI_TAG} 📊 Thiếu Bảng biểu (Table)")

            links = content_area.find_all('a', href=True)
            internal = 0
            external = 0
            for l in links:
                if "http" not in l['href'] or "instawp" in l['href']: internal += 1
                else: external += 1

            if internal < 2: data['score'] -= 5; data['issues']['Content'].append("🔗 Thiếu Link nội bộ")
            if external < 1: data['score'] -= 5; data['issues']['Content'].append("🌐 Thiếu Link ra ngoài")

            if not content_area.find_all(class_=re.compile(r'wp-block-button')):
                data['score'] -= 3; data['issues']['Content'].append("🔘 Thiếu Nút bấm")
            if not content_area.find_all(['strong', 'b']):
                data['score'] -= 3; data['issues']['Content'].append("🎨 Thiếu Bôi đậm")

            content_imgs = [img for img in content_area.find_all('img') if int(img.get('width', 100) or 100) > 50]
            if len(content_imgs) < 3:
                data['score'] -= 5; data['issues']['Content'].append("🖼️ Thêm ảnh vào (Cần >3)")

            missing_alt = sum(1 for img in content_imgs if not img.get('alt'))
            if missing_alt > 0:
                data['score'] -= 5; data['issues']['Content'].append(f"{AI_TAG} 🖼️ {missing_alt} ảnh thiếu Alt")

        else:
            data['score'] -= 50
            data['issues']['Tech'].append("⚠️ Lỗi cấu trúc: Không tìm thấy bài viết")
            data['issues']['Content'].append("❌ [PHẠT] Không kiểm tra được nội dung")

    except Exception as e:
        data['score'] = 0; data['issues']['Tech'].append(f"Lỗi: {str(e)}")

    data['final_score'] = max(0, int(data['score']))
    return data

# --- GIAO DIỆN ---
st.set_page_config(page_title="SEO Arena Final", layout="wide")

st.markdown("""
<style>
    .block-container { padding: 1rem 0.5rem; }

    .hero-card {
        background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
        color: #2c3e50; padding: 15px; border-radius: 12px; text-align: center;
        margin-bottom: 20px; border: 2px solid #fff; box-shadow: 0 0 15px rgba(241, 196, 15, 0.5);
    }
    .hero-title { font-size: 28px; font-weight: 900; margin-bottom: 5px; text-transform: uppercase; }
    .hero-quote { font-size: 18px; font-style: italic; font-weight: 700; background: rgba(255,255,255,0.3); padding: 8px; border-radius: 8px; display: inline-block; color: #2d3436; }

    .seo-card {
        background-color: #1a1c24; border: 1px solid #444; border-radius: 10px;
        padding: 12px; height: 380px; display: flex; flex-direction: column;
        margin-bottom: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .group-name { font-size: 18px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 40%; }
    .rank-badge { font-size: 12px; font-weight: bold; padding: 4px 8px; border-radius: 6px; margin: 0 5px; white-space: nowrap; }
    .score-val { font-size: 26px; font-weight: 900; color: #FFD700; margin-left: auto; }
    .progress-bg { width: 100%; height: 8px; background-color: #333; border-radius: 4px; margin-bottom: 8px; }
    .bug-container { flex-grow: 1; overflow-y: auto; padding-right: 2px; }
    .bug-container::-webkit-scrollbar { display: none; }
    .cat-header { font-size: 11px; font-weight: bold; color: #888; margin-top: 6px; margin-bottom: 2px; text-transform: uppercase; border-bottom: 1px dashed #444; }
    .bug-item { font-size: 15px; margin-bottom: 4px; display: block; padding-left: 8px; line-height: 1.4; font-weight: 500; }
    .err-tech { color: #00cec9; border-left: 3px solid #00cec9; }
    .err-pre { color: #fab1a0; border-left: 3px solid #fab1a0; }
    .err-cont { color: #ff7675; border-left: 3px solid #ff7675; }
    .clean-msg { color: #4cd137; font-weight: bold; text-align: center; font-size: 16px; margin-top: 40px; }
    .redirect-tag { font-size: 10px; color: #81ecec; border: 1px solid #81ecec; padding: 2px 4px; border-radius: 4px; margin-left: 5px; }
    .ai-tag { display: inline-block; background-color: #6c5ce7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-right: 5px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

st.title(f"🔥 SEO ARENA: {TARGET_KEYWORD}")

results = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(audit_final, g): g for g in GROUP_URLS}
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

df = pd.DataFrame(results).sort_values('final_score', ascending=False).reset_index(drop=True)

# --- HERO BANNER (TOP 1) ---
if len(df) > 0:
    top1 = df.iloc[0]
    trash_talk = get_trash_talk(top1['name'])
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-title">👑 NHÀ VÔ ĐỊCH: {top1['name']} ({top1['final_score']} ĐIỂM)</div>
        <div class="hero-quote">{trash_talk}</div>
    </div>
    """, unsafe_allow_html=True)

# --- GRID ---
def render_card(row_data):
    score = int(row_data['final_score'])
    name = row_data['name']
    issues = row_data['issues']
    is_redirected = row_data['redirected']

    if score >= 90: rank_text = "GOD"; rank_bg = "#f1c40f"; rank_color = "#000"; bar_color = "#f1c40f"
    elif score >= 70: rank_text = "PRO"; rank_bg = "#e67e22"; rank_color = "#fff"; bar_color = "#e67e22"
    elif score >= 50: rank_text = "TẬP SỰ"; rank_bg = "#3498db"; rank_color = "#fff"; bar_color = "#3498db"
    else: rank_text = "GÀ MỜ"; rank_bg = "#555"; rank_color = "#ccc"; bar_color = "#e74c3c"

    redirect_html = "<span class='redirect-tag'>🔀 Đã sửa Link</span>" if is_redirected else ""

    bugs_html = ""
    total_bugs = sum(len(v) for v in issues.values())

    # LOGIC HIỂN THỊ:
    # Nếu Perfect (0 lỗi) -> Hiện thông báo Perfect.
    # Nếu chưa Perfect (dù 95 điểm hay 100 điểm mà vẫn còn warning) -> Vẫn hiện lỗi ra.
    if total_bugs == 0:
        bugs_html = "<div class='clean-msg'>✨ PERFECT 100/100!</div>"
    else:
        if issues['Tech']:
            bugs_html += "<div class='cat-header'>TECHNICAL & URL</div>"
            for bug in issues['Tech']: bugs_html += f"<span class='bug-item err-tech'>• {bug}</span>"
        if issues['Pre']:
            bugs_html += "<div class='cat-header'>PRE-CLICK</div>"
            for bug in issues['Pre']: bugs_html += f"<span class='bug-item err-pre'>• {bug}</span>"
        if issues['Content']:
            bugs_html += "<div class='cat-header'>CONTENT & AI SEO</div>"
            for bug in issues['Content']:
                clean_bug = bug.replace("[ 🤖 AISEO ]", "")
                if "AISEO" in bug:
                    bugs_html += f"<span class='bug-item err-cont'><span class='ai-tag'>🧠 AISEO</span>{clean_bug}</span>"
                else:
                    bugs_html += f"<span class='bug-item err-cont'>• {bug}</span>"

    return f"""
    <div class="seo-card">
        <div class="card-header">
            <span class="group-name">{name}</span>
            <span class="rank-badge" style="background-color: {rank_bg}; color: {rank_color}">{rank_text}</span>
            <span class="score-val">{score}</span>
        </div>
        <div style="font-size:10px; color:#aaa; margin-top:-5px; margin-bottom:5px;">{redirect_html}</div>
        <div class="progress-bg">
            <div style="width: {score}%; height:100%; background-color: {bar_color}; border-radius:3px;"></div>
        </div>
        <div class="bug-container">
            {bugs_html}
        </div>
    </div>
    """

# Hiển thị TẤT CẢ các nhóm (Từ Top 1 -> Top 12)
row1 = st.columns(6)
for i in range(6): # Nhóm 1-6
    if i < len(df): row1[i].markdown(render_card(df.iloc[i]), unsafe_allow_html=True)

row2 = st.columns(6)
for i in range(6, 12): # Nhóm 7-12

    if i < len(df): row2[i-6].markdown(render_card(df.iloc[i]), unsafe_allow_html=True)
