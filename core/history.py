from __future__ import annotations
from typing import Optional
from supabase import create_client, Client
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

_supabase: Optional[Client] = None

def _get_supabase() -> Optional[Client]:
  global _supabase
  if _supabase is None:
    url = cfg.supabase.url
    key = cfg.supabase.key 
    if not url or not key:
      log.warning('Supabase URL or Key not set. History functionality will be disabled.')
      return None
    try:
      _supabase = create_client(url, key)
      log.info('Supabase client initialized successfully.')
    except Exception as e:
      log.error(f'Error initializing Supabase client: {e}')
      return None
  return _supabase

def get_history(user_id: str, session_id: str, limit: int = 20) -> list[dict[str, str]]:
  # Lấy limit message gần nhất của session_id từ Supabase, sắp xếp theo created_at giảm dần, sau đó đảo lại để có thứ tự thời gian tăng dần
  client = _get_supabase()
  if not client:
    return []
  
  try:
    response = client.table('chat_history') \
      .select('role', 'content') \
      .eq('user_id', user_id) \
      .eq('session_id', session_id) \
      .order('created_at', desc=True) \
      .limit(limit) \
      .execute() # chỉ lấy role và content lọc theo user_id và session_id, sắp xếp theo created_at giảm dần, giới hạn số lượng
    
    messages = response.data[::-1] # đảo lại để có thứ tự thời gian tăng dần
    log.debug(f'Fetched {len(messages)} messages from history for user_id={user_id}, session_id={session_id}')
    return messages
  except Exception as e:
    log.error(f'Error fetching history from Supabase: {e}')
    return []
  
def add_to_history(user_id: str, session_id: str, role: str, content: str) -> None:
  # Thêm message vào Supabase với user_id, session_id, role, content. created_at sẽ tự động do Supabase quản lý
  client = _get_supabase()
  if not client:
    return 
  
  try:
    client.table('chat_history').insert({
      'user_id': user_id,
      'session_id': session_id,
      'role': role,
      'content': content
    }).execute()
    log.debug(f'Added message to history for user_id={user_id}, session_id={session_id}, role={role}')
  except Exception as e:
    log.error(f'Error adding message to history in Supabase: {e}')

def reset_history(user_id: str, session_id: str) -> None:
  # Xóa tất cả message của session_id trong Supabase
  client = _get_supabase()
  if not client:
    return
  
  try:
    client.table('chat_history').delete() \
      .eq('user_id', user_id) \
      .eq('session_id', session_id) \
      .execute()
    log.info(f'Reset history for user_id={user_id}, session_id={session_id}')
  except Exception as e:
    log.error(f'Error resetting history in Supabase: {e}')

  
  
