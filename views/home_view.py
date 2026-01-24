import streamlit as st
import pandas as pd
from config import EVENT_BANNERS
from booking_and_voice_search.voice_controller import VoiceSearchController


def render_home(service):
    # 1. KHỞI TẠO CONTROLLER
    voice_controller = VoiceSearchController()
    listening_placeholder = st.empty()


    # 3. XỬ LÝ VOICE INPUT
    if st.session_state.get("fill_from_voice"):
        st.session_state["manual_search_input"] = st.session_state["voice_query"]
        st.session_state["fill_from_voice"] = False

    # 4. THANH TÌM KIẾM & MICRO
    st.markdown("<h3 class='section-title'>🎬 Khám Phá Điện Ảnh</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])

    with c1:
        search_query = st.text_input(
            "Tìm kiếm", placeholder="Tìm tên phim hoặc thể loại...",
            key="manual_search_input", label_visibility="collapsed"
        )
    with c2:
        if st.button("🎙️ Voice Search", use_container_width=True):
            listening_placeholder.info("🎧 Đang nghe... bạn nói!")
            voice_text, error = voice_controller.get_voice_query()
            listening_placeholder.empty()
            if not error:
                st.session_state["voice_query"] = voice_text
                st.session_state["fill_from_voice"] = True
                st.rerun()

    # 5. LOGIC HIỂN THỊ CHÍNH
    if search_query:
        # --- TRƯỜNG HỢP A: KẾT QUẢ TÌM KIẾM ---
        search_list, ai_list = service.get_recommendations(search_query)

        if search_list:
            st.subheader(f"🎯 Kết quả cho: '{search_query}'")
            for movie in search_list:
                render_movie_card_list(movie, "search")

        if ai_list:
            st.subheader("✨ Gợi ý tương tự cho bạn")
            for movie in ai_list:
                render_movie_card_list(movie, "ai")
    else:
        # --- TRƯỜNG HỢP B: TRANG CHỦ MẶC ĐỊNH ---

        # --- [QUAN TRỌNG] PHẦN AI GỢI Ý CÁ NHÂN HÓA ---
        if st.session_state.get('is_logged_in'):
            user_id = st.session_state.get('user_id')
            username = st.session_state.get('username')

            # Lấy list phim từ hàm AI ông vừa thêm vào Service
            rec_movies = service.get_personalized_recommendations(user_id)

            if not rec_movies.empty:
                st.markdown(f"### ✨ Dành riêng cho {username}")
                st.caption("Dựa trên lịch sử đặt vé của bạn tại Start Cinema")

                cols = st.columns(5)
                for idx, (_, movie) in enumerate(rec_movies.head(5).iterrows()):
                    with cols[idx]:
                        render_movie_card_grid(movie)
                st.divider()

        # --- PHẦN CAROUSEL PHIM TỔNG QUÁT ---
        st.markdown("### 🔥 Phim đang chiếu")
        render_carousel(service)


# --- HELPER: THẺ PHIM DẠNG LƯỚI (Cho AI Recommendations) ---
def render_movie_card_grid(movie):
    # Lấy dữ liệu an toàn cho cả Object và DataFrame
    title = movie.title if hasattr(movie, 'title') else movie['title']
    poster = movie.poster if hasattr(movie, 'poster') else movie.get('poster', '')
    m_id = movie.movieId if hasattr(movie, 'movieId') else movie['movieId']
    rating = movie.average_rating if hasattr(movie, 'average_rating') else movie.get('average_rating', 0)

    st.markdown(f"""
        <div class="movie-container">
            <div class="movie-img-box">
                <img src="{poster}" onerror="this.src='https://placehold.co/400x600?text=No+Image'">
            </div>
            <div class="movie-title" style="font-size: 14px; height: 40px;">{title}</div>
            <div style="color: #ffeb3b; font-size: 12px;">⭐ {rating:.1f}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("ĐẶT VÉ", key=f"rec_btn_{m_id}", use_container_width=True):
        st.session_state['selected_movie_id'] = m_id
        st.session_state['page'] = 'booking'
        st.rerun()

# --- HELPER FUNCTION ĐỂ RENDER THẺ PHIM TRONG DANH SÁCH TÌM KIẾM ---
def render_movie_card_list(movie, prefix):
    # Defensive check cho dữ liệu thô
    if hasattr(movie, 'rating'):
        m_title, m_rating, m_genre, m_id = movie.title, movie.rating, movie.genre, movie.id
    elif isinstance(movie, (list, tuple)):
        m_id, m_title, m_genre, m_rating = movie[0], movie[1], movie[2], f"⭐ {movie[4]}"
    else:
        return

    with st.container(border=True):
        sc2, sc3 = st.columns([4, 1.5])
        with sc2:
            st.markdown(f"**{m_title}**")
            st.caption(f"{m_rating} | {m_genre}")
            if prefix == "ai":
                st.markdown("<span style='font-size: 0.8rem; color: #00d4ff;'>AI Recommendation</span>",
                            unsafe_allow_html=True)
        with sc3:
            if st.button("Đặt vé", key=f"{prefix}_btn_{m_id}"):
                st.session_state['selected_movie_id'] = m_id
                st.session_state['selected_seats'] = []
                st.session_state['page'] = 'booking'
                st.rerun()


# --- HELPER FUNCTION ĐỂ RENDER CAROUSEL ---
def render_carousel(service):
    movies = service.get_all_movies()
    items_per_slide = 5
    total_movies = len(movies)

    if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0
    start_idx = st.session_state['movie_index']
    if start_idx >= total_movies: start_idx = 0

    end_idx = min(start_idx + items_per_slide, total_movies)
    current_movies = movies[start_idx:end_idx]

    col_prev, col_main, col_next = st.columns([0.5, 10, 0.5])

    with col_prev:
        st.markdown("<br>" * 8, unsafe_allow_html=True)
        if start_idx > 0 and st.button("❮", key="prev"):
            st.session_state['movie_index'] = max(0, start_idx - items_per_slide)
            st.rerun()

    with col_main:
        cols = st.columns(items_per_slide)
        for i in range(items_per_slide):
            with cols[i]:
                if i < len(current_movies):
                    m = current_movies[i]
                    title = m.title if hasattr(m, 'title') else "Movie"
                    poster = m.poster if hasattr(m, 'poster') else ""
                    rating = m.rating if hasattr(m, 'rating') else "⭐ 0.0"

                    st.markdown(f"""
                        <div class="movie-container">
                            <div class="movie-img-box">
                                <img src="{poster}" onerror="this.src='https://placehold.co/400x600?text=No+Image'">
                            </div>
                            <div class="movie-title">{title}</div>
                            <div class="movie-meta">
                                <span class="tag">Phim</span>
                                <span style="float: right; color: #ffeb3b;">{rating}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    m_id = m.id if hasattr(m, 'id') else i
                    if st.button("ĐẶT VÉ", key=f"btn_{m_id}", use_container_width=True):
                        st.session_state['selected_movie_id'] = m_id
                        st.session_state['selected_seats'] = []
                        st.session_state['page'] = 'booking'
                        st.rerun()

    with col_next:
        st.markdown("<br>" * 8, unsafe_allow_html=True)
        if end_idx < total_movies and st.button("❯", key="next"):
            st.session_state['movie_index'] += items_per_slide
            st.rerun()

# 2. HIỂN THỊ BANNER SLIDER (Giữ nguyên phần cũ của ông)
    imgs_html = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
    st.markdown(f"""
        <div class="slider-frame">
            <div class="slide-images">{imgs_html}</div>
            <div class="slider-overlay"></div>
        </div>
    """, unsafe_allow_html=True)