import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. Cấu hình giao diện Neon Gen Z
st.set_page_config(page_title="Z-Hunter AI v2", page_icon="⚡")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff41; }
    .stButton>button { background-color: #6200ee; color: white; border-radius: 20px; width: 100%; }
    .stTextInput>div>div>input { border: 2px solid #00ff41; background-color: #1a1c24; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Z-Hunter AI (Gemini Edition)")
st.subheader("Trợ lý săn hàng xuyên lục địa cho Gen Z")
st.write("---")

# 2. Nhập API Key Google Gemini
api_key = st.sidebar.text_input("Nhập Gemini API Key của bạn:", type="password")

# 3. Hàm lướt web tìm giá thực tế
def search_product(query):
    with DDGS() as ddgs:
        results = ddgs.text(f"{query} site:shopee.vn OR site:lazada.vn OR site:tiktok.com", max_results=3)
        return results

if api_key:
    # Cấu hình Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = st.chat_input("Dán link hoặc tên món hàng muốn săn...")
    
    if prompt:
        with st.status("🚀 Đang lướt web săn deal cho bạn..."):
            # Bước 1: AI tự đi tìm dữ liệu thực tế trên mạng
            real_data = search_product(prompt)
            
            # Bước 2: AI phân tích dữ liệu và trả lời
            context = f"Dữ liệu thực tế từ web: {real_data}"
            full_prompt = f"Bạn là Z-Hunter, chuyên gia săn deal. Dựa vào dữ liệu này: {context}, hãy tư vấn cho người dùng về món hàng: {prompt}. Dùng ngôn ngữ Gen Z Việt Nam cực cháy, tư vấn chỗ rẻ và uy tín."
            
            response = model.generate_content(full_prompt)
            answer = response.text
        
        st.chat_message("assistant").markdown(answer)
        
        # Hiển thị các link tìm được
        with st.expander("🔗 Xem các nguồn săn hàng AI tìm thấy"):
            for res in real_data:
                st.write(f"- [{res['title']}]({res['href']})")
else:
    st.info("👈 Hãy nhập Gemini API Key ở bên trái để 'đánh thức' trợ lý AI nhé!")