# Streamlit 应用入口
# ui/app.py

import streamlit as st

st.set_page_config(page_title="自训练 SpaCy 系统", layout="wide")

st.title("自训练 SpaCy 系统")

st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["文本输入", "训练数据查看", "文档管理"])

if page == "文本输入":
    from pages import text_input

    text_input.run()
elif page == "训练数据查看":
    from pages import data_view

    data_view.run()
elif page == "文档管理":
    from pages import document_manager

    document_manager.run()
