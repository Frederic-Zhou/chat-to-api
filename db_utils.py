import sqlite3
import json

# 创建或连接数据库
conn = sqlite3.connect("insight.db")
cursor = conn.cursor()


# 创建 done_insight 和 fail_insight 表
def create_tables():
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS done_insight (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at INTEGER,
        text TEXT,
        lang TEXT,
        categories TEXT,
        labels TEXT,
        result TEXT,
        train_it BOOLEAN DEFAULT 0
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS fail_insight (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at INTEGER,
        text TEXT,
        lang TEXT,
        categories TEXT,
        labels TEXT,
        result TEXT,
        train_it BOOLEAN DEFAULT 0
    )
    """
    )

    # 添加索引
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_done_created_at ON done_insight(created_at)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_done_categories ON done_insight(categories)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_done_labels ON done_insight(labels)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_done_train_it ON done_insight(train_it)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_done_lang ON done_insight(lang)")

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fail_created_at ON fail_insight(created_at)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fail_categories ON fail_insight(categories)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fail_labels ON fail_insight(labels)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_fail_train_it ON fail_insight(train_it)"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fail_lang ON fail_insight(lang)")

    conn.commit()


# 保存成功结果到 done_insight/ 保存失败结果到 fail_insight
def save_insight(timestamp, text, lang, categories, labels, result, isDone):
    categories_str = json.dumps(list(categories.keys()))  # 将分类转换为字符串
    labels_dict = {label_type: label for label, label_type in labels}
    labels_str = json.dumps(labels_dict)  # 将标签转换为字符串

    if isDone:
        table_name = "done_insight"
    else:
        table_name = "fail_insight"

    cursor.execute(
        f"""
        INSERT INTO {table_name} (created_at, text, lang, categories, labels, result)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, text, lang, categories_str, labels_str, result),
    )

    conn.commit()


# 关闭数据库连接
def close_db():
    conn.close()


# 创建表
create_tables()
