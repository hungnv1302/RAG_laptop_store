from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import pdfplumber
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

# Nhận diện được các đề mục được đánh số la mã như I Giới thiệu chung, II Tầm nhìn và sứ mệnh
_ROMAN_HEADING = re.compile(
  r"^(I{1,3}V?|V?I{0,3}|VI{1,3})\s+[A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴa-zđ]",
  re.MULTILINE
)

# Nhận diện các đề mục được đánh số như 1 Laptop Gaming, 2 Laptop Học tập - Văn phòng
_NUM_HEADING = re.compile(
  r"^(\d+)\s+[A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ]",
  re.MULTILINE
)

# Nhận diện số trang xuất hiện độc nhất 1 dòng
_PAGE_NUMBER = re.compile(r'^\d{1, 3}$')

# Các cụm không phải section
_SKIP_HEADINGS = [
  'CÔNG TY TNHH CÔNG NGHỆ',
  'HÙNG NHỮ'
]

def _classify_line(line: str) -> str | None:
  # Xác định 1 dòng bất kì có phải heading không
  stripped = line.strip()
  if not stripped:
    return None
  
  # Trả về None nếu nó nằm trong _SKIP_HEADINGS
  if stripped in _SKIP_HEADINGS:
    return None
  
  # Trả về None nếu nó được nhận diện là số trang
  if _PAGE_NUMBER.match(stripped):
    return None
  
  # Trả về chính nó nếu là đề mục được đánh bằng số la mã
  if _ROMAN_HEADING.match(stripped):
    return stripped
  
  # Trả về chính nó nếu là đề mục được đánh bằng số
  if _NUM_HEADING.match(stripped):
    return stripped
  
  return None