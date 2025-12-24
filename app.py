import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

# 1. CẤU HÌNH GIAO DIỆN HỌC TẬP
st.set_page_config(page_title="Z-Tutor AI", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 10px; }
    .stTextInput>div>div>input { border: 2px solid #4CAF50; }
    h1 { color: #2E7D32; font-family: 'Segoe UI', sans-serif; }
    .study-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Z-Tutor AI: Gia Sư 4.0")
st.write("### Hướng dẫn chi tiết • Giải bài tập • Lộ trình học tập")

# 2. LẤY API KEY TỪ SECRETS HOẶC SIDEBAR
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("🔑 Nhập Gemini API Key:", type="password")

# 3. HÀM TÌM TÀI LIỆU THAM KHẢO (Hình ảnh, Video, Link)
def search_learning_resources(query):
    try:
        with DDGS() as ddgs:
            # Tìm kiếm video và link học tập
            video_results = ddgs.text(f"video bài giảng {query} youtube", max_results=2)
            doc_results = ddgs.text(f"tài liệu học tập {query} pdf wiki", max_results=2)
            return video_results + doc_results
    except:
        return []

# 4. HÀM TỰ ĐỘNG CHỌN MODEL
def get_working_model(api_key):
    try:
        genai.configure(api_key=api_key)
        candidate_models = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-pro']
        available = [m.name.split('/')[-1] for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in candidate_models:
            if name in available: return genai.GenerativeModel(name)
        return genai.GenerativeModel(available[0])
    except: return None

# 5. GIAO DIỆN CHÍNH
if api_key:
    model = get_working_model(api_key)
    
    # Thanh bên trái cho các chức năng nhanh
    with st.sidebar:
        st.header("📌 Công cụ học tập")
        mode = st.radio("Chọn chế độ:", ["Giải bài tập chi tiết", "Lập thời khóa biểu", "Tìm tài liệu tham khảo"])
        st.info("Mẹo: Bạn có thể dán đề toán hoặc yêu cầu lập lịch học 7 ngày vào đây.")

    if model:
        # Nhập yêu cầu từ học sinh
        user_input = st.chat_input("Nhập bài tập hoặc môn học bạn cần hỗ trợ...")
        
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
                
            with st.status("🧠 Gia sư AI đang suy nghĩ...", expanded=True) as status:
                # Tìm tài liệu bổ trợ
                st.write("📚 Đang tìm video và tài liệu liên quan...")
                resources = search_learning_resources(user_input)
                
                # Tạo nội dung hướng dẫn
                st.write("✍️ Đang soạn bài giảng chi tiết...")
                prompt = f"""
                Bạn là Z-Tutor, một gia sư tận tâm và thông thái. 
                Nhiệm vụ: {mode} cho câu hỏi: '{user_input}'.
                Yêu cầu:
                1. Nếu là giải bài: Hãy giải từng bước một (step-by-step), giải thích lý thuyết tại sao lại làm vậy.
                2. Nếu là thời khóa biểu: Hãy lập lịch học khoa học, có thời gian nghỉ ngơi (Pomodoro).
                3. Giọng văn: Thân thiện, khuyến khích học sinh.
                4. Sử dụng Markdown để trình bày đẹp mắt (in đậm, bảng, danh sách).
                """
                
                response = model.generate_content(prompt)
                status.update(label="✅ Đã hoàn thành bài giảng!", state="complete", expanded=False)
            
            # Hiển thị kết quả
            with st.chat_message("assistant"):
                st.markdown(response.text)
                
                if resources:
                    st.markdown("---")
                    st.subheader("🔗 Tài liệu tham khảo bổ trợ (Video & Link):")
                    for res in resources:
                        st.write(f"- [{res['title']}]({res['href']})")
    else:
        st.error("API Key không hợp lệ hoặc không có quyền truy cập Gemini.")
else:
    st.info("👈 Hãy đảm bảo bạn đã nhập API Key ở Secrets hoặc Sidebar để gặp Gia sư AI!")

st.markdown("---")
st.caption("Z-Tutor AI v3.0 • Giúp bạn học tập thông minh hơn mỗi ngày")
