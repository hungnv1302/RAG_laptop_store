from __future__ import annotations
import logging
import logging.config
from pathlib import Path
from xml.sax import handler
import yaml

_LOGGING_CONF = Path(__file__).resolve().parent.parent / 'config' / 'logging.yaml'
_configured = False

def _setup():
  global _configured #đảm bảo chỉ cấu hình logging một lần
  if _configured:
    return
  
  with open(_LOGGING_CONF, 'r', encoding='utf-8') as f:
    conf = yaml.safe_load(f)

    #đảm bảo thư mục logs tồn tại
    handlers = conf.get('handlers', {})
    for h_name, h_conf in handlers.items():
      filename = h_conf.get('filename')
      if filename:
        log_path = Path(filename)
        log_path.parent.mkdir(parents = True, exist_ok = True)
    
    logging.config.dictConfig(conf)
    _configured = True

def get_logger(name: str) -> logging.Logger:
  _setup()
  return logging.getLogger(name)