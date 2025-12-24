import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. CẤU HÌNH GIAO DIỆN (UI)
st.set_page_config(page_title="Z-Hunter AI", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #f0f2f6; }
    h1 { color: #00ff41; text-shadow: 0 0 10px #00ff41; }
    .stStatusWidget { border-radius: 15px; border: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Z-Hunter AI")
st.write("### Trợ lý săn deal chuyên nghiệp")

# 2. LẤY API KEY TỪ SECRETS HOẶC SIDEBAR
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("🔑 Nhập Gemini API Key:", type="password")

# 3. HÀM TÌM KIẾM DỮ LIỆU THỰC TẾ
def search_product(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(f"{query} giá bao nhiêu shopee lazada tiktokvn", max_results=3)
            return results
    except:
        return []

# 4. HÀM TỰ ĐỘNG CHỌN MODEL PHÙ HỢP
def get_working_model(api_key):
    genai.configure(api_key=api_key)
    # Danh sách ưu tiên các model từ mạnh đến nhẹ
    candidate_models = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-pro']
    
    try:
        # Lấy danh sách thực tế mà tài khoản của bạn được phép dùng
        available = [m.name.split('/')[-1] for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Chọn model đầu tiên có trong danh sách khả dụng của bạn
        for model_name in candidate_models:
            if model_name in available:
                return genai.GenerativeModel(model_name)
        
        # Nếu không khớp tên nào, lấy cái đầu tiên trong danh sách khả dụng
        return genai.GenerativeModel(available[0])
    except Exception as e:
        st.error(f"Lỗi khi kiểm tra Model: {e}")
        return None

# 5. CHƯƠNG TRÌNH CHÍNH
if api_key:
    model = get_working_model(api_key)
    
    if model:
        prompt = st.chat_input("Dán link hoặc tên món hàng...")
        
        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
                
            with st.status("🚀 Đang check giá thị trường...", expanded=True) as status:
                st.write("🔍 Đang lướt web tìm kèo...")
                real_data = search_product(prompt)
                
                st.write(f"🧠 AI đang phân tích bằng {model.model_name}...")
                context = f"Dữ liệu thực tế: {real_data}"
                full_prompt = (
                    f"Bạn là Z-Hunter, chuyên gia săn deal. Dựa vào dữ liệu: {context}, "
                    f"hãy tư vấn về: '{prompt}'. Dùng ngôn ngữ Gen Z cháy, tư vấn ngắn gọn."
                )
                
                try:
                    response = model.generate_content(full_prompt)
                    status.update(label="✅ Đã tìm thấy kèo!", state="complete", expanded=False)
                    
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    
                    if real_data:
                        with st.expander("🔗 Xem nguồn tham khảo"):
                            for res in real_data:
                                st.write(f"- [{res['title']}]({res['href']})")
                except Exception as e:
                    st.error(f"AI không phản hồi: {e}")
else:
    st.info("👈 Hãy dán API Key vào thanh bên trái hoặc cài đặt trong Secrets để bắt đầu!")

st.markdown("---")
st.caption("Z-Hunter AI v2.1 • Cập nhật tự động Model")
