# 文档管理页面
# ui/pages/document_manager.py

import streamlit as st
import os
from app.config.settings import settings


def run():
    st.header("文档管理")

    # 显示已有的文档列表
    files = os.listdir(settings.DOCUMENTS_DIR)
    st.subheader("已有文档")
    selected_file = st.selectbox("选择文档", files)

    if selected_file:
        file_path = os.path.join(settings.DOCUMENTS_DIR, selected_file)
        if selected_file.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = st.text_area("编辑文档内容：", content, height=300)
            if st.button("保存修改"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                st.success("文档已保存，索引正在更新...")
                # 调用函数更新 LlamaIndex 索引
                from app.services.llama_index import init_index

                init_index()
        else:
            st.warning("该文件不是文本文件，无法编辑。")

    # 上传新文档
    st.subheader("上传新文档")
    uploaded_file = st.file_uploader(
        "选择文件", type=["txt", "pdf", "png", "jpg", "jpeg", "mp4", "mp3"]
    )
    if uploaded_file:
        save_path = os.path.join(settings.DOCUMENTS_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"文件 {uploaded_file.name} 已上传。")
        # 处理非文本文件（如图片、音频），提取文本内容
        if uploaded_file.type.startswith("image"):
            from app.utils.ocr import image_to_text

            text = image_to_text(save_path)
            text_file = save_path + ".txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(text)
        # 更新 LlamaIndex 索引
        from app.services.llama_index import init_index

        init_index()
