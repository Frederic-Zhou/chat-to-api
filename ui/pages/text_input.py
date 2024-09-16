# ui/pages/text_input.py

import streamlit as st
import requests


def run():
    st.header("文本输入")
    text = st.text_area("请输入文本：", height=200)
    if st.button("提交"):
        if text.strip():
            response = requests.post("http://localhost:8000/send", json={"text": text})
            if response.status_code == 200:
                st.success("文本已提交。")
            else:
                st.error(f"提交失败：{response.text}")
        else:
            st.warning("请输入文本后再提交。")
