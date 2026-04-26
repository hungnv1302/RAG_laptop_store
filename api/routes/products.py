import json
import re
from fastapi import APIRouter, HTTPException

from config.settings import cfg
from core.logger import get_logger
from core.models import Product
from api.schemas import (
  UpdatePriceRequest,
  UpdateStockRequest,
  BatchUpdatePriceRequest,
  BatchUpdateStockRequest,
  AddProductRequest
)
from vector_store import (
  get_collection_count,
  update_price as store_update_price,
  update_stock as store_update_stock,
  add_product_to_collection
)
from vector_store.client import _get_client
from embedding.embedder import embed_texts
from ingestion.processor import product_to_text, product_to_metadata
from qdrant_client.models import FieldCondition, Filter, MatchValue

router = APIRouter(tags = ['Products'])
log = get_logger(__name__)

@router.get('/stats')
async def get_stats():
  # Lấy những thông số cơ bản về collection 
  try:
    client = _get_client()
    coll = cfg.qdrant.knowledge_collection

    product_result = client.count(
      collection_name=coll,
      count_filter = Filter(must=[FieldCondition(key='type', match=MatchValue(value='product'))]),
      exact=True
    )
    company_result = client.count(
      collection_name=coll,
      count_filter=Filter(must=[FieldCondition(key='type', match=MatchValue(value='company'))]),
      exact=True
    )
    total = get_collection_count(coll)
    return {
      'total_count': total,
      'product_count': product_result.count,
      'company_chunks': company_result.count,
      'status': 'indexed'
    }
  except Exception as e:
    return {
      'total_count': 0,
      'product_chunks': 0,
      'company_chunks': 0,
      'status': f'error: {e}'
    }

@router.put('/update-price')
async def update_price(req: UpdatePriceRequest):
  success = store_update_price(cfg.qdrant.knowledge_collection, req.product_id, req.new_price)
  if not success:
    raise HTTPException(404, f'Product {req.product_id} not found')
  return {
    'status': 'ok',
    'product_id': req.product_id,
    'new_price': req.new_price
  }

@router.put('/update-price/batch')
async def batch_update_price(req: BatchUpdatePriceRequest):
  results = {}
  for pid, price in req.updates.items():
    results[pid] = store_update_price(cfg.qdrant.knowledge_collection, pid, price)
  return {'status': 'ok', 'results': results}

@router.put('/update-stock')
async def update_stock(req: UpdateStockRequest):
  success = store_update_stock(cfg.qdrant.knowledge_collection, req.product_id, req.new_stock)
  if not success:
    raise HTTPException(404, f'Product {req.product_id} not found')
  return {
    'status': 'ok',
    'product_id': req.product_id,
    'new_stock': req.new_stock
  }

@router.put('/update-stock/batch')
async def batch_update_stock(req: BatchUpdateStockRequest):
  results = {}
  for pid, stock in req.updates.items():
    results[pid] = store_update_stock(cfg.qdrant.knowledge_collection, pid, stock)
  return {'status': 'ok', 'results': results}

@router.post('/add-product')
async def add_product(req: AddProductRequest):
  json_path = cfg.paths.json_path
  if json_path.exists():
    with open(json_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
  else:
    data = []

  # Tự động tạo id nếu không được cung cấp
  product_id = req.id
  if not product_id:
    max_id = 0
    for item in data:
      match = re.search(r'PROD_(\d+)', item.get('id', ''))
      if match:
        max_id = max(max_id, int(match.group(1)))
    product_id = f'PROD_{max_id + 1:03d}'
    log.info(f'Auto-generated product_id: {product_id}')
  log.info(f'Adding product with id: {product_id} - {req.name}')

  try:
    product = Product(
      id=product_id,
      name=req.name, 
      brand=req.brand,
      price=req.price,
      currency=req.currency,
      category=req.category,
      specs=req.specs,
      stock=req.stock,
      image_url=req.image_url,
      product_url=req.product_url,
      description=req.description
    )

    text = product_to_text(product)
    metadata = product_to_metadata(product)
    
    embedding = embed_texts(text)

    metadata['type'] = 'product'

    add_product_to_collection(
      collection_name=cfg.qdrant.knowledge_collection,
      product_id=product.id,
      text=text,
      embedding=embedding,
      metadata=metadata
    )

    data.append(product.model_dump())
    with open(json_path, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
    
    return {
      'status': 'ok',
      'product_id': product.id,
      'message': f'Product {product.name} added successfully'
    }
  except Exception as e:
    log.error(f'Error adding product: {e}')
    raise HTTPException(status_code=500, detail=str(e))
