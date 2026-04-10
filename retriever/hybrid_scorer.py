from __future__ import annotations
from typing import Any
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

def compute_hybrid_scores(candidates: list[dict[str, Any]], alpha: float | None = None) -> list[dict[str, Any]]:
  # Sắp xếp candidates theo điểm hybrid 
  if alpha is None:
    alpha = cfg.retrieval.hybrid_alpha

  for c in candidates:
    vec_score = c.get('vector_score', 0.0)
    bm25_score = c.get('bm25_score', 0.0)
    c['hybrid_score'] = alpha * vec_score + (1-alpha) * bm25_score

  candidates.sort(key=lambda x: x['hybrid_score'], reverse=True)

  log.debug(f'Hybrid scores computed (alpha = {alpha})')
  return candidates