import streamlit as st
from services import CinemaService
from views.components import inject_custom_css, render_header, render_footer
from views.home_view import render_home
from views.booking_view import render_booking
from views.login_view import render_login

# --- CẤU HÌNH ---
st.set_page_config(page_title="Cinema AI System", page_icon="🍿", layout="wide")

# --- KHỞI TẠO STATE ---
if 'page' not in st.session_state: st.session_state['page'] = 'home'
if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0
if 'selected_movie_id' not in st.session_state: st.session_state['selected_movie_id'] = None
if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""

def main():
    # 1. Load CSS & Header
    inject_custom_css()

    # 2. Khởi tạo Service (Backend)
    service = CinemaService()

    # 3. Điều hướng trang (Routing)
    if st.session_state['page'] == 'login':
        render_login() # Lưu ý: file login không cần Header vì nó tự render riêng
    else:
        render_header() # Header chung cho Home và Booking

        if st.session_state['page'] == 'home':
            render_home(service)
        elif st.session_state['page'] == 'booking':
            render_booking(service)

        render_footer()

if __name__ == "__main__":
    main()