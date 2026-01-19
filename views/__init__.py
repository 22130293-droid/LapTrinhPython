import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Copy toàn bộ nội dung trong thẻ <style> từ code cũ vào đây */
        .stApp { background: radial-gradient(circle at top, #1b1b2f 0%, #16213e 50%, #0f3460 100%); color: #FFFFFF; }
        /* ... (Để tiết kiệm dòng hiển thị, bạn copy phần CSS dài ở code cũ vào đây nhé) ... */
        </style>
    """, unsafe_allow_html=True)

def render_header():
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
    st.markdown("""
        <div class="footer">
            <p>&copy; 2026 START CINEMA AI SYSTEM.</p>
        </div>
    """, unsafe_allow_html=True)