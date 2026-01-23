import streamlit as st
import pandas as pd
from config import EVENT_BANNERS
from booking_and_voice_search.voice_controller import VoiceSearchController


def render_home(service):
    # 1. Khởi tạo Voice Controller
    voice_controller = VoiceSearchController()

    # 2. HIỂN THỊ BANNER SLIDER
    imgs_html = "".join([f'<div class="img-container"><img src="{url}"></div>' for url in EVENT_BANNERS])
    st.markdown(f"""
        <div class="slider-frame">
            <div class="slide-images">{imgs_html}</div>
            <div class="slider-overlay"></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. XỬ LÝ VOICE INPUT
    listening_placeholder = st.empty()
    if st.session_state.get("fill_from_voice"):
        st.session_state["manual_search_input"] = st.session_state["voice_query"]
        st.session_state["fill_from_voice"] = False

    # 4. THANH TÌM KIẾM
    st.markdown("<h3 class='section-title'>🔥 Phim Đang Chiếu</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1.5])
    with c2:
        col_in, col_btn = st.columns([5, 1])
        search_query = col_in.text_input(
            "Search",
            placeholder="🔍 Tìm tên phim...",
            key="manual_search_input",
            label_visibility="collapsed"
        )
        with col_btn:
            if st.button("🎙️", key="mic_btn"):
                listening_placeholder.info("🎧 Đang nghe...")
                voice_text, error = voice_controller.get_voice_query()
                listening_placeholder.empty()
                if error:
                    st.toast(error, icon="⚠️")
                else:
                    st.session_state["voice_query"] = voice_text
                    st.session_state["fill_from_voice"] = True
                    st.rerun()

    # 5. LOGIC HIỂN THỊ

    if search_query:
        with c1:
            # GIẢ ĐỊNH: service.get_recommendations trả về (list_search, list_ai)
            search_list, ai_list = service.get_recommendations(search_query)

            # --- PHẦN 1: KẾT QUẢ TÌM KIẾM CHÍNH XÁC ---
            if search_list:
                st.markdown(f"#### 🎯 Kết quả tìm kiếm cho: *'{search_query}'*")
                for movie in search_list:
                    render_movie_card(movie, "search")

            # --- KẺ VẠCH NGĂN CÁCH ---
            if search_list and ai_list:
                st.divider()

            # --- PHẦN 2: PHIM AI GỢI Ý ---
            if ai_list:
                st.markdown(f"#### ✨ Phim gợi ý tương tự")
                for movie in ai_list:
                    render_movie_card(movie, "ai")

            if not search_list and not ai_list:
                st.info("Không tìm thấy phim nào phù hợp với yêu cầu của bạn.")

    else:
        # --- TRƯỜNG HỢP B: HIỆN CAROUSEL (Dữ liệu mặc định) ---
        render_carousel(service)


# --- HELPER FUNCTION ĐỂ RENDER THẺ PHIM TRONG DANH SÁCH TÌM KIẾM ---
def render_movie_card(movie, prefix):
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