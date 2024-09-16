# 模型训练逻辑
# app/services/model_trainer.py

import spacy
from spacy.util import minibatch, compounding
import random
import os
from app.utils.db import SessionLocal
from app.models.schemas import TextData
from app.config.settings import settings


def train_model():
    nlp = spacy.blank("zh")  # 创建空的中文模型

    # 添加 NER 组件
    ner = nlp.create_pipe("ner")
    nlp.add_pipe("ner", last=True)

    # 从数据库中加载已标记未训练的数据
    with SessionLocal() as session:
        data = (
            session.query(TextData).filter(TextData.status == "labeled_untrained").all()
        )

    TRAIN_DATA = []
    for item in data:
        entities = []
        for label, value in item.labels.items():
            start = item.text.find(value)
            if start != -1:
                end = start + len(value)
                entities.append((start, end, label))
        TRAIN_DATA.append((item.text, {"entities": entities}))

    # 添加标签到 NER
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # 开始训练
    optimizer = nlp.begin_training()
    for itn in range(10):
        random.shuffle(TRAIN_DATA)
        batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
        losses = {}
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(texts, annotations, sgd=optimizer, losses=losses)
        print(f"Iteration {itn}, Losses: {losses}")

    # 保存模型
    model_version = get_new_model_version()
    output_dir = os.path.join(settings.MODEL_DIR, model_version)
    nlp.to_disk(output_dir)
    print(f"模型已保存到 {output_dir}")

    # 更新数据状态为已训练
    with SessionLocal() as session:
        for item in data:
            item.status = "trained"
        session.commit()


def get_new_model_version():
    model_dir = settings.MODEL_DIR
    versions = [int(d) for d in os.listdir(model_dir) if d.isdigit()]
    if versions:
        new_version = str(max(versions) + 1)
    else:
        new_version = "1"
    return new_version
