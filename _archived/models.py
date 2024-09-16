import config
import os
import spacy
from spacy.cli import download
import time

# 初始化模型字典（全局变量）
models = {}  # 用于保存更新后的模型

# 确保模型目录存在
if not os.path.exists(config.MODEL_DIR):
    os.makedirs(config.MODEL_DIR)


# 创建空模型并添加必要管道的函数
def create_blank_model(lang):
    nlp = spacy.blank(lang)  # 创建空白模型
    if "ner" not in nlp.pipe_names:
        nlp.add_pipe("ner")
    if "textcat" not in nlp.pipe_names:
        nlp.add_pipe("textcat")
    print(f"空白模型 {lang} 已创建，并添加了管道: {nlp.pipe_names}")
    return nlp


# 预加载所有支持的语言模型
def preload_models():
    global models  # 使用全局的 models 变量
    for lang, model_name in config.MODEL_LANGS.items():
        model_path = os.path.join(config.MODEL_DIR, model_name)
        if not os.path.exists(model_path):
            # 如果下载失败，创建空白模型
            print(f"{model_name}，正在创建空白模型 {lang}")
            nlp = create_blank_model(lang)
            # 将模型保存到指定路径
            nlp.to_disk(model_path)

        models[lang] = spacy.load(model_path)
    print(f"所有模型已加载: {list(models.keys())}")


# 保存更新后的模型，并只重新加载更新的语言模型
def save_updated_model(nlp, lang):
    global models  # 确保访问全局 models 变量
    model_name = config.MODEL_LANGS[lang]
    model_path = os.path.join(config.MODEL_DIR, model_name)  # 同样的保存路径
    nlp.to_disk(model_path)  # 保存模型
    models[lang] = spacy.load(model_path)  # 重新加载更新后的模型
    print(f"模型 {lang} 已保存到: {model_path}")
    return model_path  # 返回路径用于重新加载
