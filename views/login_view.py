# views/login_view.py
import streamlit as st
import time as et
from config import TEST_USER, TEST_PASS
from views.components import render_header

def render_login():
    # Gọi header tại đây vì trang login đứng độc lập
    render_header()

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="background: linear-gradient(to right, #ff416c, #ff4b2b); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">WELCOME BACK</h2>
                <p>Vui lòng đăng nhập để tiếp tục</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="admin")
            password = st.text_input("Mật khẩu", type="password", placeholder="123")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("ĐĂNG NHẬP NGAY", type="primary", use_container_width=True)

            if submitted:
                if username == TEST_USER and password == TEST_PASS:
                    st.session_state['is_logged_in'] = True
                    st.session_state['username'] = username
                    st.success("Đăng nhập thành công!")
                    et.sleep(0.5)
                    # Điều hướng về trang trước đó
                    st.session_state['page'] = st.session_state.get('pre_login_page', 'home')
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")