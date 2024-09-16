import os

def create_project_structure(project_root):
    directories = [
        'app',
        'app/api',
        'app/models',
        'app/services',
        'app/utils',
        'app/config',
        'app/templates',  # 如果需要前端模板
        'ui',
        'ui/pages',
        'ui/components',
        'models',          # 保存训练的 SpaCy 模型
        'documents',       # LlamaIndex 文档存储目录
        'data',            # 数据文件（如训练数据集）
    ]

    files = {
        'app/__init__.py': '',
        'app/main.py': '# FastAPI 应用入口',
        'app/api/__init__.py': '',
        'app/api/endpoints.py': '# 定义 API 路由和处理函数',
        'app/models/__init__.py': '',
        'app/models/schemas.py': '# 定义数据模型和 Pydantic 模型',
        'app/services/__init__.py': '',
        'app/services/text_processor.py': '# 文本处理和预测逻辑',
        'app/services/model_trainer.py': '# 模型训练逻辑',
        'app/services/llama_index.py': '# 与 LlamaIndex 的交互',
        'app/services/handler_caller.py': '# 处理函数调用逻辑',
        'app/utils/__init__.py': '',
        'app/utils/db.py': '# 数据库连接和操作',
        'app/utils/rabbitmq.py': '# RabbitMQ 连接和操作',
        'app/utils/ocr.py': '# OCR 处理（如果需要）',
        'app/config/__init__.py': '',
        'app/config/settings.py': '# 配置项',
        'ui/app.py': '# Streamlit 应用入口',
        'ui/pages/data_view.py': '# 训练数据查看页面',
        'ui/pages/document_manager.py': '# 文档管理页面',
        'requirements.txt': '',
        'README.md': '# 项目说明文档',
        '.env': '',  # 环境变量配置文件
    }

    for directory in directories:
        dir_path = os.path.join(project_root, directory)
        os.makedirs(dir_path, exist_ok=True)
        print(f'创建目录: {dir_path}')

    for file_path, content in files.items():
        full_path = os.path.join(project_root, file_path)
        # 确保父目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'创建文件: {full_path}')

if __name__ == '__main__':
    # 设定项目根目录为当前目录
    project_root = os.getcwd()
    create_project_structure(project_root)
    print('项目文件结构已创建完成。')