import config
import os
import spacy
from spacy.lookups import Lookups
from spacy.cli import download

# 初始化模型字典（全局变量）
models = {}

# 确保模型目录存在
if not os.path.exists(config.MODEL_DIR):
    os.makedirs(config.MODEL_DIR)


# 预加载所有支持的语言模型
def preload_models():
    global models  # 使用全局的 models 变量
    models = {}
    for lang, model_name in config.MODEL_LANGS.items():
        model_path = os.path.join(config.MODEL_DIR, model_name)
        if not os.path.exists(model_path):
            download(model_name)
            nlp = spacy.load(model_name)
            nlp.to_disk(model_path)

        models[lang] = spacy.load(model_path)
    print(f"所有模型已加载: {list(models.keys())}")


# 保存更新后的模型，并自动重新加载模型
def save_updated_model(nlp, lang):
    global models  # 确保访问全局 models 变量
    model_name = config.MODEL_LANGS[lang]
    model_path = os.path.join(config.MODEL_DIR, model_name)  # 同样的保存路径
    nlp.to_disk(model_path)  # 保存模型
    print(f"模型 {lang} 已保存到: {model_path}")

    # 自动重载语言模型
    preload_models()  # 调用函数重载模型
    print(f"所有模型已重新加载。")
    return model_path  # 返回路径用于重新加载


preload_models()
