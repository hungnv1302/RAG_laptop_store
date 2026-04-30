import streamlit as st
from ui.auth import render_auth_form, render_user_info
from ui.api_client import post_reset, get_stats, get_history

def render_sidebar() -> None:
  with st.sidebar:
    st.title('Hùng Nhữ laptop')

    # Authentication
    if not st.session_state.auth_token:
      render_auth_form()
    else:
      render_user_info()
      # Load lịch sử từ db nếu st.session_state.messages đang trống
      if not st.session_state.messages:
        with st.spinner('Đang tải lịch sử...'):
          history = get_history(
            session_id = st.session_state.session_id,
            token = st.session_state.auth_token
          )
          st.session_state.messages = history
          if history:
            st.rerun()
    st.divider()

    # Reser chat
    if st.button('Reset Chat', use_container_width=True):
      post_reset(
        session_id = st.session_state.session_id,
        token = st.session_state.auth_token
      )
      st.session_state.messages = []
      st.rerun()

    st.divider()

    # Stats
    stats = get_stats()
    if stats:
      st.metric('Tổng dữ liệu', stats.get('total_count', 0))
      st.metric('Sản phẩm', stats.get('product_count', 0))
      st.metric('Thông tin shop', stats.get('company_chunks', 0))
    else:
      st.info('Chưa kết nối được API')
    
    st.divider()

    # Gợi ý câu hỏi
    st.markdown(
      """
**Gợi ý câu hỏi:**
- Laptop gaming dưới 30 triệu
- Laptop đồ họa RTX 5070
- Laptop văn phòng nhẹ
- So sánh Lenovo và Asus
- Shop ở đâu?
"""
    )
