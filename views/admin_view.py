import streamlit as st
import plotly.express as px
import pandas as pd


def render_admin_dashboard(movie_df, admin_service):
    st.markdown("<h1 style='text-align: center; color: #E50914;'>🛡️ QUẢN TRỊ HỆ THỐNG CINEMA</h1>",
                unsafe_allow_html=True)
    st.markdown("---")

    # 1. LẤY DỮ LIỆU
    real_revenue, total_sold, movie_summary, daily_summary = admin_service.get_booking_stats()
    avg_rating = movie_df['average_rating'].mean()
    total_movies = len(movie_df)

    # 2. KHỐI CHỈ SỐ TỔNG QUAN (METRICS)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("💰 Tổng doanh thu", f"{real_revenue:,.0f} đ")
    with m2:
        st.metric("🎟️ Vé đã bán", f"{total_sold} vé")
    with m3:
        st.metric("⭐ Rating TB", f"{avg_rating:.2f}")
    with m4:
        st.metric("🎬 Tổng phim", f"{total_movies}")

    st.write("")

    # 3. KHỐI BIỂU ĐỒ THEO TUẦN (7 NGÀY)
    st.subheader("📊 Thống kê hiệu suất 7 ngày gần nhất")

    if daily_summary:
        # Chuyển đổi dict sang DataFrame
        df_daily = pd.DataFrame.from_dict(daily_summary, orient='index').reset_index()
        df_daily.columns = ['Ngày', 'Doanh Thu', 'Số Vé']

        # Chỉ lấy 7 ngày gần nhất (Tail 7)
        df_daily = df_daily.tail(7)

        col_left, col_right = st.columns(2)

        with col_left:
            # Biểu đồ cột Doanh thu
            fig_rev = px.bar(
                df_daily, x='Ngày', y='Doanh Thu',
                title="Doanh thu mỗi ngày",
                text_auto='.2s',  # Hiện số rút gọn (vd: 1.2M) trên đầu cột
                color_discrete_sequence=['#E50914']
            )
            fig_rev.update_xaxes(type='category')
            fig_rev.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                height=350,
                xaxis_title=None
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        with col_right:
            # Biểu đồ cột Số vé
            fig_tix = px.bar(
                df_daily, x='Ngày', y='Số Vé',
                title="Lượng vé bán ra mỗi ngày",
                text_auto=True,
                color_discrete_sequence=['#ff8c00']
            )
            fig_rev.update_xaxes(type='category')

            fig_tix.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                height=350,
                xaxis_title=None
            )
            st.plotly_chart(fig_tix, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu giao dịch theo ngày.")

    st.divider()

    # 4. CÁC BIỂU ĐỒ CŨ (THỂ LOẠI & RATING)
    col_1, col_2 = st.columns(2)
    with col_1:
        st.subheader("🎬 Tỷ lệ Thể loại")
        genre_data = admin_service.get_genre_distribution()
        if not genre_data.empty:
            fig_pie = px.pie(names=genre_data.index, values=genre_data.values, hole=0.5,
                             color_discrete_sequence=px.colors.sequential.Reds_r)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=300,
                                  margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_2:
        st.subheader("📈 Phân bổ Rating")
        rating_data = admin_service.get_rating_stats()
        if not rating_data.empty:
            fig_rating = px.bar(x=rating_data.index, y=rating_data.values, color_continuous_scale='Reds')
            fig_rating.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                                     height=300)
            st.plotly_chart(fig_rating, use_container_width=True)

    st.divider()

    # 5. BẢNG DỮ LIỆU PHIM
    st.subheader("📂 Danh sách kho phim")
    search_term = st.text_input("Tìm kiếm phim nhanh...", placeholder="Nhập tên phim...")

    display_df = movie_df.copy()
    if search_term:
        display_df = display_df[display_df['title'].str.contains(search_term, case=False)]

    st.dataframe(
        display_df[['movieId', 'title', 'genres', 'average_rating', 'rating_count']].head(50),
        use_container_width=True, hide_index=True
    )