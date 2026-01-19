# views/booking_view.py
import streamlit as st
import time as et
from booking_and_voice_search.booking_serveice import check_availability, save_booking

def render_booking(service):
    # Lấy thông tin phim đang chọn từ session_state
    if not st.session_state.get('selected_movie_id'):
        st.error("Chưa chọn phim nào!")
        if st.button("Quay lại trang chủ"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    # Lấy object movie từ service
    movie = service.get_movie_by_id(st.session_state['selected_movie_id'])

    if not movie:
        st.error("Không tìm thấy thông tin phim!")
        if st.button("Quay lại"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    if st.button("⬅ QUAY LẠI TRANG CHỦ", key="back_home"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_L, col_R = st.columns([1, 2], gap="large")

    with col_L:
        # INFO BOX - Hiển thị thông tin phim
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="display: flex; gap: 20px; align-items: center;">
                    <img src="{movie.poster}" style="width: 110px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);">
                    <div>
                        <h2 style="margin: 0; font-size: 24px; background: linear-gradient(to right, #ff9966, #ff5e62); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{movie.title}</h2>
                        <p style="margin-top: 10px; font-size: 14px; color: #aaa;">⏱ Thời lượng: {movie.duration}<br>🎭 Thể loại: {movie.genre}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("📅 CHỌN SUẤT CHIẾU")
        # Lấy lịch chiếu từ service
        days = list(service.showtimes.keys())
        # Nếu chưa có ngày chọn, mặc định ngày đầu tiên
        if 'selected_date' not in st.session_state or st.session_state['selected_date'] not in days:
            st.session_state['selected_date'] = days[0]

        s_day = st.selectbox("Chọn Ngày", days, index=days.index(st.session_state['selected_date']), label_visibility="collapsed")
        st.session_state['selected_date'] = s_day

        st.markdown("---")
        times = service.showtimes.get(s_day, [])
        s_time = st.radio("Chọn Giờ", times, horizontal=True)
        st.session_state['selected_time'] = s_time

        # Tính tiền
        count = len(st.session_state['selected_seats'])
        total = count * movie.price

        # BILL BOX - Hóa đơn
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 25px; border-radius: 15px; margin-top: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: linear-gradient(90deg, #ff416c, #ff4b2b);"></div>
            <div style="text-align: center; font-weight: 900; letter-spacing: 2px; font-size: 18px; margin-bottom: 20px; color: #16213e;">TICKET RECEIPT</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #666;">Phim</span>
                <strong style="color: #333;">{movie.title[:18]}...</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #666;">Ghế</span>
                <strong style="color: #333;">{', '.join(st.session_state['selected_seats']) if count else '--'}</strong>
            </div>
             <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #666;">Giá vé</span>
                <strong style="color: #333;">{movie.price:,.0f} đ</strong>
            </div>
            <hr style="border-top: 2px dashed #ccc; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 24px; font-weight: 800;">
                <span style="color: #16213e;">TỔNG</span>
                <span style="color: #ff4b2b;">{total:,.0f} đ</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if count > 0:
            st.write("")
            if st.button("💳 THANH TOÁN NGAY", type="primary", use_container_width=True):
                if not st.session_state.get('is_logged_in'):
                    st.warning("⚠️ Bạn cần đăng nhập để thanh toán!")
                    et.sleep(1)
                    st.session_state['pre_login_page'] = 'booking'
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    # Kiểm tra ghế trống
                    if not check_availability(movie.id, s_day, s_time, st.session_state['selected_seats']):
                        st.error("Ghế đã có người đặt! Vui lòng chọn ghế khác.")
                    else:
                        # Lưu booking
                        save_booking(movie.id, s_day, s_time, st.session_state['selected_seats'])
                        st.session_state['selected_seats'] = []
                        st.balloons()
                        st.success(f"Cảm ơn {st.session_state['username']}! Vé đã được gửi tới email.")
                        et.sleep(2)
                        st.session_state['page'] = 'home'
                        st.rerun()

    with col_R:
        # MÀN HÌNH CONG GIẢ LẬP
        st.markdown("""
            <div style="perspective: 1000px; margin-bottom: 40px; text-align: center;">
                <div style="
                    width: 80%; margin: 0 auto; height: 10px; 
                    background: #fff; 
                    box-shadow: 0 20px 50px rgba(255,255,255,0.2); 
                    border-radius: 50%; 
                    transform: rotateX(-5deg);">
                </div>
                <div style="margin-top: 10px; color: #666; font-size: 12px; letter-spacing: 5px;">MÀN HÌNH</div>
            </div>
        """, unsafe_allow_html=True)

        # Lấy sơ đồ ghế từ service
        layout = service.get_seat_layout(movie.id, st.session_state['selected_date'], st.session_state['selected_time'])

        # Vẽ ghế
        with st.container():
            for r, row in enumerate(layout):
                cols = st.columns([1.5] + [1]*8 + [1.5]) # Căn giữa lưới ghế
                for c, status in enumerate(row):
                    seat_id = f"{chr(65 + r)}{c + 1}"
                    with cols[c+1]:
                        if status == 1:
                            st.button(f"{seat_id}", key=seat_id, disabled=True)
                        elif seat_id in st.session_state['selected_seats']:
                            if st.button(f"✓ {seat_id}", key=seat_id, type="primary"):
                                st.session_state['selected_seats'].remove(seat_id)
                                st.rerun()
                        else:
                            if st.button(f"{seat_id}", key=seat_id):
                                st.session_state['selected_seats'].append(seat_id)
                                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)
        xc1, xc2, xc3, xc4, xc5 = st.columns([1, 2, 2, 2, 1])
        with xc2: st.markdown("⬜ **Trống**")
        with xc3: st.markdown("🔒 **Đã đặt**")
        with xc4: st.markdown("🔴 **Đang chọn**")