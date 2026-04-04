from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
  id: str
  name: str
  brand: str
  price: int
  currency: str = "VNĐ"
  category: list[str] = Field(default_factory=list) #mỗi sản phẩm có một list riêng 
  specs: dict[str, str] = Field(default_factory=dict) #mỗi sản phẩm có một dict riêng
  stock: int = 0
  image_url: str = ""
  product_url: str = ""
  description: str = ""

class RetrievedDoc(BaseModel):
  text: str
  metadata: dict[str, Any]
  score: float = 0.0
  source_type: str = "product" #hoặc "company"
