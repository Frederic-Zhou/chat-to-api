import sqlite3
import spacy
from spacy.training import Example
import json

# 连接到数据库
conn = sqlite3.connect("insight.db")
cursor = conn.cursor()


# 从数据库中获取需要训练的数据
def get_training_data():
    cursor.execute("SELECT text, lang FROM fail_insight WHERE train_it = 1")
    return cursor.fetchall()


# 将数据标记为已训练
def mark_as_trained():
    cursor.execute("UPDATE fail_insight SET train_it = 0 WHERE train_it = 1")
    conn.commit()


# 执行增量训练
def incremental_training():
    # 获取需要训练的数据
    training_data = get_training_data()

    if not training_data:
        print("没有可用于增量训练的数据。")
        return

    # 按语言进行分组
    lang_data_map = {}
    for text, lang in training_data:
        if lang not in lang_data_map:
            lang_data_map[lang] = []
        lang_data_map[lang].append(text)

    # 对每种语言的数据进行增量训练
    for lang, texts in lang_data_map.items():
        try:
            print(f"开始对 {lang} 的模型进行增量训练...")

            # 加载模型
            if lang == "en":
                nlp = spacy.load("en_core_web_lg")
            elif lang == "zh":
                nlp = spacy.load("zh_core_web_lg")
            else:
                nlp = spacy.load(f"{lang}_core_web_sm")  # 使用默认 sm 模型

            # 创建训练示例
            examples = []
            for text in texts:
                doc = nlp.make_doc(text)
                example = Example.from_dict(
                    doc, {"entities": []}
                )  # 根据需要定义 entities
                examples.append(example)

            # 进行增量训练
            optimizer = nlp.initialize()
            for i in range(10):  # 迭代10次
                losses = {}
                nlp.update(examples, sgd=optimizer, losses=losses)
                print(f"Iteration {i}, Losses: {losses}")

            # 保存更新后的模型
            nlp.to_disk(f"updated_model_{lang}")
            print(f"模型 {lang} 已完成增量训练并保存。")

        except Exception as e:
            print(f"对 {lang} 的模型进行增量训练时出错: {e}")

    # 标记数据为已训练
    mark_as_trained()


# 关闭数据库连接
def close_db():
    conn.close()


# 执行增量训练
if __name__ == "__main__":
    incremental_training()
    close_db()
