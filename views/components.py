import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Roboto:wght@300;400;700&display=swap');
        
        /* --- GLOBAL THEME --- */
        .stApp { 
            background: radial-gradient(circle at top, #1b1b2f 0%, #16213e 50%, #0f3460 100%); 
            color: #FFFFFF; 
            font-family: 'Montserrat', sans-serif; 
        }
        
        h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; text-shadow: 0 4px 6px rgba(0,0,0,0.3); font-weight: 800 !important; }
        p, span, div, label { color: #e0e0e0; }

        /* ==========================================================================================
           1. FIX MÀU CHỮ SELECTBOX (Hộp chọn ngày) - MỚI THÊM
           ========================================================================================== */
        /* Chỉnh màu chữ hiển thị trong ô chọn thành ĐEN để dễ đọc trên nền trắng */
        div[data-baseweb="select"] > div {
            color: #000000 !important;
            background-color: #ffffff !important;
            font-weight: 600 !important;
        }
        /* Chỉnh màu chữ trong danh sách xổ xuống */
        div[role="listbox"] li {
            color: #000000 !important;
        }
        /* Chỉnh icon mũi tên trong selectbox */
        div[data-baseweb="select"] svg {
            fill: #000000 !important;
        }

        /* --- CUSTOM BUTTONS (Nút chung - Login, Submit...) --- */
        div.stButton > button {
            background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);
            color: white !important;
            border: none;
            border-radius: 25px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(229, 45, 39, 0.4);
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229, 45, 39, 0.6);
        }
        /* Nút phụ (Secondary) */
        div.stButton > button[kind="secondary"] {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.3);
            box-shadow: none;
        }

        /* ==========================================================================================
           2. BOOKING SEATS (GHẾ NGỒI) 
           Target cụ thể vào nút trong cột để hạn chế ảnh hưởng nút khác
           ========================================================================================== */
        div[data-testid="column"] button {
            padding: 0px !important;
            min-height: 40px !important;
            border-radius: 8px 8px 15px 15px !important; 
            margin: 2px !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            transition: all 0.2s;
        }

        /* TRẠNG THÁI 1: GHẾ TRỐNG (Mặc định - Secondary) */
        div[data-testid="column"] button[kind="secondary"] {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
        }
        div[data-testid="column"] button[kind="secondary"]:hover {
            border-color: #ff4b2b !important;
        }

        /* TRẠNG THÁI 2: GHẾ ĐANG CHỌN (Primary - Đổi sang XANH LÁ) */
        div[data-testid="column"] button[kind="primary"] {
            background: #2ecc71 !important; /* Xanh lá */
            border: 1px solid #27ae60 !important;
            color: white !important;
            box-shadow: 0 0 10px rgba(46, 204, 113, 0.6) !important; 
            transform: scale(1.05);
        }
        div[data-testid="column"] button[kind="primary"]:hover {
            background: #27ae60 !important;
        }

        /* TRẠNG THÁI 3: GHẾ ĐÃ MUA (Disabled - Đổi sang ĐỎ ĐẬM) */
        div[data-testid="column"] button:disabled {
            background-color: #d32f2f !important; /* Đỏ Đậm */
            color: #ffffff !important;             
            border: 1px solid #b71c1c !important;  
            opacity: 1 !important;                 /* QUAN TRỌNG: Hiển thị rõ 100%, không bị mờ */
            cursor: not-allowed;
            text-decoration: line-through;         
        }

        /* --- HEADER GLASSMORPHISM --- */
        .header-container {
            display: flex; justify-content: space-between; align-items: center;
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        .logo { 
            font-size: 32px; font-weight: 900; letter-spacing: 2px;
            background: linear-gradient(to right, #ff416c, #ff4b2b); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            text-decoration: none !important; 
        }

        /* --- BANNER SLIDER --- */
        .slider-frame { 
            overflow: hidden; 
            width: 100%; 
            aspect-ratio: 21/9; 
            max-height: 550px;
            margin-bottom: 50px; 
            border-radius: 20px; 
            position: relative; 
            box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
            border: 1px solid rgba(255,255,255,0.1); 
        }
        .slide-images { 
            width: 300%; height: 100%; display: flex; 
            animation: slide_animation 18s infinite cubic-bezier(0.45, 0, 0.55, 1); 
        }
        .img-container { width: 100%; height: 100%; position: relative; }
        .img-container img { 
            width: 100%; height: 100%; 
            object-fit: cover; 
            object-position: center 20%; 
        }
        
        @keyframes slide_animation { 
            0%, 28% { margin-left: 0%; } 
            33%, 61% { margin-left: -100%; } 
            66%, 94% { margin-left: -200%; } 
            100% { margin-left: 0%; } 
        }

        /* --- MOVIE CARD --- */
        .movie-container { 
            background: rgba(255, 255, 255, 0.05); 
            backdrop-filter: blur(5px);
            border-radius: 16px; padding: 12px; 
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            height: 100%; 
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .movie-container:hover { 
            transform: translateY(-10px) scale(1.02); 
            border-color: #ff4b2b; 
            box-shadow: 0 15px 30px rgba(255, 75, 43, 0.2); 
            background: rgba(255, 255, 255, 0.1);
        }
        .movie-img-box { 
            border-radius: 12px; overflow: hidden; margin-bottom: 12px; 
            aspect-ratio: 2/3; 
            position: relative; 
            width: 100%;
        }
        .movie-img-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
        .movie-container:hover .movie-img-box img { transform: scale(1.1); }
        
        .movie-title { font-family: 'Montserrat', sans-serif; font-size: 16px; font-weight: 700; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFF; }
        .tag { background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; font-size: 11px; color: #bbb; border: 1px solid rgba(255,255,255,0.1); }

        /* --- FOOTER --- */
        .footer {
            margin-top: 80px;
            padding: 40px 20px;
            background: rgba(0,0,0,0.3);
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            font-size: 14px;
            color: #888;
        }
        .footer a { color: #ff4b2b; text-decoration: none; font-weight: bold; margin: 0 10px; transition: 0.3s; }
        .footer a:hover { color: #fff; text-shadow: 0 0 10px #ff4b2b; }
        .footer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 1000px; margin: 0 auto 30px auto; text-align: left; }
        .footer-col h4 { color: #fff; margin-bottom: 15px; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }

        /* --- INPUT FIELDS --- */
        div[data-testid="stTextInput"] input {
            background-color: rgba(255,255,255,0.1);
            color: white;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #ff4b2b;
            box-shadow: 0 0 10px rgba(255, 75, 43, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    # ... (Giữ nguyên code render_header của bạn)
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1.5])

        with c1: st.markdown('<a href="#" class="logo">🍿 START CINEMA</a>', unsafe_allow_html=True)

        with c2:
            if st.button("TRANG CHỦ", key="nav_home"):
                st.session_state['page'] = 'home'
                st.rerun()
        with c3: st.button("LỊCH CHIẾU", key="nav_event")

        with c4:
            if st.button("THÀNH VIÊN", key="nav_member"):
                if st.session_state.get('is_logged_in'):
                    st.toast(f"Xin chào: {st.session_state['username']}")
                else:
                    st.session_state['pre_login_page'] = 'home'
                    st.session_state['page'] = 'login'
                    st.rerun()

        with c5:
            if st.session_state.get('is_logged_in'):
                if st.button(f"Logout ({st.session_state['username']})", key="logout_btn"):
                    st.session_state['is_logged_in'] = False
                    st.session_state['username'] = ""
                    st.rerun()
            else:
                if st.button("🔐 ĐĂNG NHẬP", key="login_btn_header"):
                    st.session_state['pre_login_page'] = 'home'
                    st.session_state['page'] = 'login'
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_footer():
    # ... (Giữ nguyên code render_footer của bạn)
    st.markdown("""
        <div class="footer">
            <div class="footer-grid">
                <div class="footer-col">
                    <h4>Về Start Cinema</h4>
                    <p>Hệ thống rạp chiếu phim hiện đại hàng đầu với công nghệ AI gợi ý phim thông minh và trải nghiệm đặt vé mượt mà.</p>
                </div>
                <div class="footer-col">
                    <h4>Liên kết nhanh</h4>
                    <p><a href="#">Tuyển dụng</a></p>
                    <p><a href="#">Điều khoản sử dụng</a></p>
                    <p><a href="#">Chính sách bảo mật</a></p>
                </div>
                <div class="footer-col">
                    <h4>Liên hệ</h4>
                    <p>📍 Dĩ An, Bình Dương, Vietnam</p>
                    <p>📞 1900 1234</p>
                    <p>📧 support@startcinema.vn</p>
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 20px;">
            <p>&copy; 2026 START CINEMA AI SYSTEM. All rights reserved.</p>
            <div>
                <a href="#">Facebook</a> • <a href="#">Instagram</a> • <a href="#">Youtube</a>
            </div>
        </div>
    """, unsafe_allow_html=True)