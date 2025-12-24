import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. CẤU HÌNH GIAO DIỆN (UI)
st.set_page_config(page_title="Z-Hunter AI v2", page_icon="⚡", layout="centered")

# CSS tạo phong cách Neon Gen Z
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    .stChatInput { bottom: 20px; }
    .stStatusWidget { border-radius: 15px; border: 1px solid #00ff41; }
    h1 { color: #00ff41; text-shadow: 0 0 10px #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Z-Hunter AI")
st.write("### Trợ lý săn deal xuyên lục địa")

# 2. KIỂM TRA API KEY (Ưu tiên lấy từ Secrets)
api_key = None

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Nếu chưa cài Secrets thì hiện ô nhập ở sidebar để bạn dùng tạm/test
    api_key = st.sidebar.text_input("🔑 Nhập Gemini API Key để kích hoạt:", type="password")
    st.sidebar.info("Mẹo: Hãy cài API Key vào phần 'Secrets' trên Streamlit Cloud để dùng vĩnh viễn.")

# 3. HÀM TÌM KIẾM THÔNG TIN THỰC TẾ
def search_product(query):
    try:
        with DDGS() as ddgs:
            # Tìm kiếm trên các sàn TMĐT phổ biến tại Việt Nam
            search_query = f"{query} giá bao nhiêu shopee lazada tiktok"
            results = ddgs.text(search_query, max_results=3)
            return results
    except Exception as e:
        st.error(f"Lỗi tìm kiếm: {e}")
        return []

# 4. CHƯƠNG TRÌNH CHÍNH
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Sử dụng bản flash-latest để ổn định nhất trên Cloud
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Nhận câu hỏi từ người dùng
        prompt = st.chat_input("Dán link hoặc tên món hàng muốn săn...")
        
        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.status("🚀 Đang check giá thị trường...", expanded=True) as status:
                # Bước 1: Tìm dữ liệu thật
                st.write("🔍 Đang lướt Shopee, Lazada, TikTok...")
                real_data = search_product(prompt)
                
                # Bước 2: AI phân tích
                st.write("🧠 AI đang phân tích kèo thơm...")
                context = f"Dữ liệu thực tế vừa tìm được: {real_data}"
                full_prompt = (
                    f"Bạn là Z-Hunter, một chuyên gia săn deal cực khét cho Gen Z. "
                    f"Dựa vào dữ liệu này: {context}, hãy tư vấn về món hàng: '{prompt}'. "
                    f"Yêu cầu: Trả lời ngắn gọn, dùng ngôn ngữ Gen Z (vibe cháy, dùng từ như 'kèo thơm', 'múc ngay', 'đỉnh nóc kịch trần'). "
                    f"Nếu thấy giá tốt hãy khuyên dùng, nếu thấy lừa đảo hãy cảnh báo."
                )
                
                response = model.generate_content(full_prompt)
                status.update(label="✅ Đã tìm thấy kèo ngon!", state="complete", expanded=False)
            
            # Hiển thị câu trả lời của AI
            with st.chat_message("assistant"):
                st.markdown(response.text)
            
            # Hiển thị các link tham khảo
            if real_data:
                with st.expander("🔗 Xem các nguồn săn hàng AI tìm thấy"):
                    for res in real_data:
                        st.write(f"- [{res['title']}]({res['href']})")
                        
    except Exception as e:
        st.error(f"Lỗi AI: {e}")
else:
    st.warning("⚠️ Chào bạn! App chưa được cài đặt 'Chìa khóa' (API Key). Hãy nhập vào sidebar bên trái hoặc cài trong Secrets nhé.")

# 5. HƯỚNG DẪN DƯỚI CHÂN TRANG
st.markdown("---")
st.caption("Build by Gemini 3 Flash • Dữ liệu cập nhật thời gian thực")
