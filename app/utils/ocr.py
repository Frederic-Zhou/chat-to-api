# OCR 处理（如果需要）
# app/utils/ocr.py

import pytesseract
from PIL import Image


def image_to_text(image_path):
    try:
        text = pytesseract.image_to_string(
            Image.open(image_path), lang="chi_sim"
        )  # 使用中文简体
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return None
