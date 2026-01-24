import streamlit as st
import pandas as pd
from booking_and_voice_search.booking_serveice import get_user_history_json


def render_profile(service):
    # Nút quay lại
    if st.button("⬅ QUAY LẠI TRANG CHỦ", key="back_from_profile"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: white;'>HỒ SƠ CỦA TÔI</h1>", unsafe_allow_html=True)

    # Lấy thông tin user từ session
    username = st.session_state.get('username', 'Khách hàng')
    user_id = st.session_state.get('user_id', 0)
    email = st.session_state.get('email', 'Chưa cập nhật')

    # Chia Tab
    tab_info, tab_history = st.tabs(["👤 THÔNG TIN CHUNG", "🎟️ LỊCH SỬ ĐẶT VÉ"])

    with tab_info:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 20px;">
                    <div style="font-size: 80px;">👤</div>
                    <h3 style="margin: 10px 0;">{username}</h3>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
                    <p><b>Họ và tên:</b> {username}</p>
                    <p><b>Email:</b> {email}</p>
                    <p><b>Ngày tham gia:</b> 25/01/2026</p>
                </div>
            """, unsafe_allow_html=True)


    with tab_history:
        history_data = get_user_history_json(user_id)

        if not history_data:
            st.info("Bạn chưa đặt vé nào !")
        else:
            for ticket in history_data:
                movie = service.get_movie_by_id(int(ticket['movie_id']))
                movie_title = movie.title if movie else f"Phim ID: {ticket['movie_id']}"

                poster_url = movie.poster_url if movie and hasattr(movie,
                                                                   'poster_url') else "https://via.placeholder.com/100x150"

                st.markdown(f"""
                    <div style="background: white; color: #333; padding: 15px; border-radius: 12px; margin-bottom: 15px; 
                                border-left: 10px solid #ff4b2b; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <div style="flex-grow: 1;">
                            <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Mã vé: {ticket['booking_id']}</div>
                            <div style="font-size: 18px; font-weight: bold; color: #16213e; margin-bottom: 4px;">{movie_title}</div>
                            <div style="font-size: 13px; color: #555;">📅 {ticket['date']} | ⏰ {ticket['time']}</div>
                            <div style="font-size: 13px; color: #555;">💺 Ghế: <b style="color: #ff4b2b;">{ticket['seat']}</b></div>
                        </div>
                        <div style="text-align: right; min-width: 100px;">
                            <div style="font-size: 18px; font-weight: 800; color: #ff4b2b;">{ticket['price']:,.0f}đ</div>
                            <div style="font-size: 10px; background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 8px;">ĐÃ XÁC NHẬN</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)