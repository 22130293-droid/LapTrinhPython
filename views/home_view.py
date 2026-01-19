import streamlit as st
import pandas as pd
from config import EVENT_BANNERS
from booking_and_voice_search.voice_controller import VoiceSearchController

def render_home(service):
    # 1. Khởi tạo Voice Controller
    # (Lưu ý: Nếu muốn tối ưu có thể truyền từ main vào, nhưng để ở đây cũng ổn)
    voice_controller = VoiceSearchController()

    # 2. HIỂN THỊ BANNER SLIDER
    # HTML này phụ thuộc vào CSS trong styles.py/components.py.
    # Hãy chắc chắn main.py đã gọi inject_custom_css()
    imgs_html = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
    st.markdown(f"""
        <div class="slider-frame">
            <div class="slide-images">{imgs_html}</div>
            <div style="position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(180deg, rgba(27,27,47,0.2) 0%, rgba(27,27,47,0) 50%, rgba(15,52,96,0.6) 100%); pointer-events: none;"></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. XỬ LÝ VOICE INPUT (Tự động điền vào ô tìm kiếm)
    listening_placeholder = st.empty()
    if st.session_state.get("fill_from_voice"):
        st.session_state["manual_search_input"] = st.session_state["voice_query"]
        st.session_state["fill_from_voice"] = False

    # 4. THANH TÌM KIẾM
    st.markdown("<h3 style='margin-bottom: 20px; border-left: 5px solid #ff4b2b; padding-left: 15px; text-transform: uppercase; letter-spacing: 1px;'>🔥 Phim Đang Chiếu</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1.5])
    with c2:
        col_in, col_btn = st.columns([5, 1])
        # Input tìm kiếm
        search_query = col_in.text_input("Search", placeholder="🔍 Tìm tên phim...", key="manual_search_input", label_visibility="collapsed")
        # Nút Mic
        with col_btn:
            if st.button("🎙️", key="mic_btn"):
                listening_placeholder.info("🎧 Đang nghe...")
                voice_text, error = voice_controller.get_voice_query()
                listening_placeholder.empty()
                if error:
                    listening_placeholder.warning(error)
                else:
                    st.session_state["voice_query"] = voice_text
                    st.session_state["fill_from_voice"] = True
                    st.rerun()

    # 5. LOGIC HIỂN THỊ: TÌM KIẾM HOẶC CAROUSEL

    # --- TRƯỜNG HỢP A: ĐANG TÌM KIẾM ---
    if search_query:
        with c1:
            st.markdown(f"##### 🔎 Kết quả tìm kiếm cho: *'{search_query}'*")
            # Service trả về DataFrame
            recs = service.get_recommendations(search_query)

            if isinstance(recs, pd.DataFrame) and not recs.empty:
                for _, row in recs.iterrows():
                    with st.container(border=True):
                        sc2, sc3 = st.columns([4, 1.5])
                        with sc2:
                            st.markdown(f"**{row['title']}**")
                            # Xử lý genres để tránh lỗi nếu dữ liệu null
                            genres = str(row['genres']).replace('|', ', ') if 'genres' in row else "N/A"
                            rating = row['average_rating'] if 'average_rating' in row else 0.0
                            st.caption(f"⭐ {rating:.1f} | {genres}")
                        with sc3:
                            st.write("") # Spacer căn chỉnh nút xuống dưới
                            if st.button("Đặt vé", key=f"s_btn_{row['movieId']}"):
                                st.session_state['selected_movie_id'] = row['movieId']
                                st.session_state['selected_seats'] = []
                                st.session_state['page'] = 'booking'
                                st.rerun()
            elif isinstance(recs, list) and recs:
                st.warning(recs[0])
            else:
                st.info("Không tìm thấy phim phù hợp.")

    # --- TRƯỜNG HỢP B: KHÔNG TÌM KIẾM (HIỆN CAROUSEL) ---
    else:
        # Service trả về List các Object Movie
        movies = service.get_all_movies()

        # Pagination Logic
        items_per_slide = 5
        total_movies = len(movies)

        # Đảm bảo index nằm trong giới hạn
        if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0

        start_idx = st.session_state['movie_index']
        # Fix lỗi nếu start_idx vượt quá số lượng phim (do lọc hoặc data thay đổi)
        if start_idx >= total_movies: start_idx = 0

        end_idx = min(start_idx + items_per_slide, total_movies)
        current_movies = movies[start_idx:end_idx]

        col_prev, col_main, col_next = st.columns([0.5, 10, 0.5]) # Chỉnh lại tỉ lệ cột cho cân đối hơn

        # Nút Previous
        with col_prev:
            st.markdown("<br>"*8, unsafe_allow_html=True) # Căn giữa nút theo chiều dọc
            if start_idx > 0:
                if st.button("❮", key="prev"):
                    st.session_state['movie_index'] = max(0, start_idx - items_per_slide)
                    st.rerun()

        # Hiển thị List Phim
        with col_main:
            # Tạo lưới hiển thị phim (5 cột)
            cols = st.columns(items_per_slide)

            # Duyệt qua các cột, nếu phim ít hơn 5 thì các cột thừa sẽ trống
            for i in range(items_per_slide):
                with cols[i]:
                    if i < len(current_movies):
                        movie = current_movies[i]
                        # RENDER CARD HTML
                        # Class 'movie-container', 'movie-img-box' phải có trong styles.py
                        st.markdown(f"""
                            <div class="movie-container">
                                <div class="movie-img-box">
                                    <img src="{movie.poster}" onerror="this.src='https://placehold.co/400x600?text=No+Image'">
                                </div>
                                <div class="movie-title" title="{movie.title}">{movie.title}</div>
                                <div class="movie-meta">
                                    <span class="tag">{movie.genre.split(',')[0] if movie.genre else 'Phim'}</span>
                                    <span style="float: right; color: #ffeb3b; font-weight: bold;">{movie.rating}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                        st.write("") # Khoảng cách nhỏ giữa card và nút
                        if st.button("ĐẶT VÉ", key=f"btn_{movie.id}", use_container_width=True):
                            st.session_state['selected_movie_id'] = movie.id
                            st.session_state['selected_seats'] = []
                            st.session_state['page'] = 'booking'
                            st.rerun()

        # Nút Next
        with col_next:
            st.markdown("<br>"*8, unsafe_allow_html=True)
            if end_idx < total_movies:
                if st.button("❯", key="next"):
                    st.session_state['movie_index'] += items_per_slide
                    st.rerun()