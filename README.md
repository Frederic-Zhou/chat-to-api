# 项目说明文档

## 文档结构

project_root/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py       # 定义 API 路由和处理函数
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # 定义数据模型和 Pydantic 模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── text_processor.py  # 文本处理和预测逻辑
│   │   ├── model_trainer.py   # 模型训练逻辑
│   │   ├── llama_index.py     # 与 LlamaIndex 的交互
│   │   └── handler_caller.py  # 处理函数调用逻辑
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db.py              # 数据库连接和操作
│   │   ├── rabbitmq.py        # RabbitMQ 连接和操作
│   │   └── ocr.py             # OCR 处理（如果需要）
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # 配置项
│   └── templates/             # 前端模板（如果需要）
├── ui/
│   ├── app.py                 # Streamlit 应用入口
│   ├── pages/                 # Streamlit 多页面
│   │   ├── data_view.py       # 训练数据查看页面
│   │   └── document_manager.py# 文档管理页面
│   └── components/            # 自定义组件
├── models/                    # 保存训练的 SpaCy 模型
├── documents/                 # LlamaIndex 文档存储目录
├── data/                      # 数据文件（如训练数据集）
├── requirements.txt           # 项目依赖包列表
├── README.md                  # 项目说明文档
└── .env                       # 环境变量配置文件