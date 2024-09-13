import sqlite3
import spacy
from spacy.training import Example
import json
import config  # 从系统配置中导入数据库连接
import os
from db_utils import get_training_data, mark_as_trained  # 导入数据库保存函数
from spacy.lookups import Lookups


# 动态添加 textcat 和 ner 标签
def add_dynamic_labels(textcat, ner, categories, labels):
    # 动态添加 textcat 标签
    if textcat is not None:
        for category in categories.keys():  # categories 是 dict，取 keys 作为标签
            if category not in textcat.labels:
                textcat.add_label(category)
                print(f"Added TextCategorizer label: {category}")
            else:
                print(f"TextCategorizer label already exists: {category}")
    else:
        print("TextCategorizer pipe not found.")

    # 动态添加 ner 标签
    if ner is not None:
        for label_type in labels.keys():  # labels 是 dict，取 keys 作为标签
            if label_type not in ner.labels:
                ner.add_label(label_type)
                print(f"Added NER label: {label_type}")
            else:
                print(f"NER label already exists: {label_type}")
    else:
        print("NER pipe not found.")


# 查找实体在文本中的位置
def find_entity_positions(text, labels):
    entities = []
    for label_type, label_value in labels.items():
        start = text.find(label_value)
        if start != -1:
            end = start + len(label_value)
            entities.append((start, end, label_type))
    return entities


# 保存更新后的模型
def save_updated_model(nlp, lang):
    model_name = config.MODEL_LANGS[lang]
    model_path = os.path.join(config.MODEL_DIR, model_name)  # 同样的保存路径
    nlp.to_disk(model_path)  # 保存模型
    print(f"模型 {lang} 已保存到: {model_path}")
    return model_path  # 返回路径用于重新加载


# 执行增量训练
def incremental_training():
    # 获取需要训练的数据
    training_data = get_training_data()

    if not training_data:
        print("没有可用于增量训练的数据。")
        return

    # 按语言进行分组
    lang_data_map = {}
    for text, lang, categories_str, labels_str in training_data:
        categories = json.loads(categories_str)
        labels = json.loads(labels_str)

        if lang not in lang_data_map:
            lang_data_map[lang] = []
        lang_data_map[lang].append((text, categories, labels))

    # 对每种语言的数据进行增量训练
    for lang, texts in lang_data_map.items():
        try:
            print(f"开始对 {lang} 的模型进行增量训练...")

            # 加载模型
            model_name = config.MODEL_LANGS[lang]
            model_path = os.path.join(config.MODEL_DIR, model_name)
            nlp = spacy.load(model_path)
            nlp.vocab.lookups = Lookups()

            # 确保 NER 和 textcat 管道存在
            if "ner" not in nlp.pipe_names:
                ner = nlp.add_pipe("ner", last=True)
            else:
                ner = nlp.get_pipe("ner")

            if "textcat_multilabel" not in nlp.pipe_names:
                textcat = nlp.add_pipe("textcat_multilabel", last=True)
            else:
                textcat = nlp.get_pipe("textcat_multilabel")

            # 创建训练示例
            examples = []
            for text, categories, labels in texts:
                add_dynamic_labels(textcat, ner, categories, labels)
                doc = nlp.make_doc(text)

                # 查找实体在文本中的位置
                entities = find_entity_positions(text, labels)

                # 创建NER和TextCats训练示例
                example = Example.from_dict(
                    doc, {"entities": entities, "cats": categories}
                )

                print(f"entities: {entities}, cats: {categories}")
                examples.append(example)

            # 进行增量训练
            optimizer = nlp.initialize()
            for i in range(100):  # 迭代10次
                losses = {}
                nlp.update(examples, sgd=optimizer, drop=0.5, losses=losses)
                print(f"Iteration {i}, Losses: {losses}")

            # 保存更新后的模型
            model_path = save_updated_model(nlp, lang)  # 保存并获取路径
            print(f"模型 {lang} 已完成增量训练并保存。")
            # 标记数据为已训练
            mark_as_trained()
        except Exception as e:
            print(f"对 {lang} 的模型进行增量训练时出错: {e}")


# 执行增量训练
if __name__ == "__main__":
    incremental_training()
