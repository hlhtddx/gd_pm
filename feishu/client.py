import os

import lark_oapi as lk

_debug = os.environ.get('DEBUG', default=False)
_log_level = lk.LogLevel.DEBUG if _debug else lk.LogLevel.WARNING

client = lk.Client.builder() \
    .app_id(os.getenv("APP_ID")) \
    .app_secret(os.getenv("APP_SECRET")) \
    .domain(lk.FEISHU_DOMAIN) \
    .log_level(_log_level) \
    .build()
