import streamlit as st


def inject_styles() -> None:
  """Chèn toàn bộ custom CSS vào trang."""
  st.markdown(
      """
<style>
  .route-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75em;
    font-weight: 600;
    margin-bottom: 5px;
  }
  .route-product  { background: #e3f2fd; color: #1565c0; }
  .route-chitchat { background: #f3e5f5; color: #7b1fa2; }
  .route-company  { background: #e8f5e9; color: #2e7d32; }

  .product-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 12px;
    margin: 8px 0;
    background: #fafafa;
  }
  .product-card img {
    max-width: 100%;
    border-radius: 8px;
  }
  .stChatMessage {
    max-width: 100%;
  }
</style>
""",
    unsafe_allow_html=True,
  )