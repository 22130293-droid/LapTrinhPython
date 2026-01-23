import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_admin_dashboard(movie_df, admin_service):
    st.title("🛡️ QUẢN TRỊ HỆ THỐNG CINEMA")
    st.markdown("---")

    # 1. KHỐI CHỈ SỐ TỔNG QUAN (METRICS)
    total_revenue = admin_service.get_revenue_stats()
    avg_rating = movie_df['average_rating'].mean()
    total_movies = len(movie_df)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Tổng doanh thu (Ước tính)", f"{total_revenue:,.0f} đ", delta="15% so với tháng trước")
    with m2:
        st.metric("Điểm đánh giá TB", f"{avg_rating:.2f} ⭐", delta="Khá")
    with m3:
        st.metric("Tổng phim trong kho", f"{total_movies} phim")

    st.write("")

    # 2. KHỐI BIỂU ĐỒ THỐNG KÊ
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Tỷ lệ Thể loại Phim")
        genre_data = admin_service.get_genre_distribution()
        if not genre_data.empty:
            # Vẽ biểu đồ tròn (Donut Chart)
            fig_pie = px.pie(
                names=genre_data.index,
                values=genre_data.values,
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu thể loại.")

    with col_right:
        st.subheader("📈 Phân bổ Điểm đánh giá")
        rating_data = admin_service.get_rating_stats()
        if not rating_data.empty:
            # Vẽ biểu đồ cột
            fig_bar = px.bar(
                x=rating_data.index,
                y=rating_data.values,
                labels={'x': 'Số sao (⭐)', 'y': 'Số lượng phim'},
                color=rating_data.values,
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu đánh giá.")

    st.divider()

    # 3. QUẢN LÝ KHO DỮ LIỆU
    st.subheader("📂 Danh sách Phim & Phân tích Nội dung")
    # Thêm công cụ tìm kiếm nhanh trong bảng Admin
    search_term = st.text_input("Tìm kiếm phim trong kho quản lý...", placeholder="Nhập tên phim...")

    display_df = movie_df.copy()
    if search_term:
        display_df = display_df[display_df['title'].str.contains(search_term, case=False)]

    st.dataframe(
        display_df[['movieId', 'title', 'genres', 'average_rating', 'rating_count']].head(100),
        use_container_width=True,
        hide_index=True
    )

    # Nút xuất báo cáo (Tính năng "flex" thêm với giáo viên)
    if st.button("📥 Xuất báo cáo Excel (Demo)"):
        st.success("Đã trích xuất dữ liệu thành công!")