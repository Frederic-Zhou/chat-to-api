# 训练数据查看页面
# ui/pages/data_view.py

import streamlit as st
import pandas as pd
from sqlalchemy import func
from app.utils.db import SessionLocal
from app.models.schemas import TextData


def run():
    st.header("训练数据查看")

    # 统计数据
    with SessionLocal() as session:
        total_processed = (
            session.query(func.count(TextData.id))
            .filter(TextData.status == "processed")
            .scalar()
        )
        total_failed = (
            session.query(func.count(TextData.id))
            .filter(TextData.status == "failed")
            .scalar()
        )
        total_labeled_trained = (
            session.query(func.count(TextData.id))
            .filter(TextData.status == "trained")
            .scalar()
        )
        total_labeled_untrained = (
            session.query(func.count(TextData.id))
            .filter(TextData.status == "labeled_untrained")
            .scalar()
        )
        total_unlabeled = (
            session.query(func.count(TextData.id))
            .filter(TextData.status == "unlabeled")
            .scalar()
        )

    st.subheader("统计信息")
    st.write(f"调用接口成功的数据：{total_processed}")
    st.write(f"调用接口失败的数据：{total_failed}")

    # 显示饼图
    pie_data = pd.DataFrame(
        {
            "状态": ["已标记已训练", "已标记未训练", "未标记"],
            "数量": [total_labeled_trained, total_labeled_untrained, total_unlabeled],
        }
    )
    st.subheader("标记状态分布")
    st.pyplot(
        pie_data.set_index("状态").plot.pie(y="数量", autopct="%1.1f%%").get_figure()
    )

    # 列表界面
    st.subheader("数据列表")
    status_option = st.selectbox(
        "选择数据状态",
        ["processed", "failed", "trained", "labeled_untrained", "unlabeled"],
    )
    with SessionLocal() as session:
        data = session.query(TextData).filter(TextData.status == status_option).all()
    df = pd.DataFrame(
        [
            {
                "ID": d.id,
                "文本": d.text,
                "分类": d.textcat,
                "标签": d.labels,
                "状态": d.status,
                "创建时间": d.created_at,
                "更新时间": d.updated_at,
            }
            for d in data
        ]
    )
    st.dataframe(df)
