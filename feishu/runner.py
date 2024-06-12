from functools import wraps

from utils import logger
from .auth import Authentication

ERR_CODE_TOKEN_EXPIRED = 99991677
RETRY_TIMES = 3


class LarkCallArguments:
    auth: Authentication or None

    def __init__(self, auth):
        self.auth = auth
        self.config = None
        self.user_access_token = None
        self.service = None


def lark_call(service_factory, uses_user_token=True):
    def outer(func):
        @wraps(func)
        def inner(auth, *args, **kargs):
            largs = LarkCallArguments(auth)
            largs.config = auth.config
            largs.user_access_token = auth.user_access_token if uses_user_token else None
            largs.service = service_factory(largs.config)

            for retry_count in range(RETRY_TIMES):
                if uses_user_token and not largs.user_access_token and not auth.login():
                    auth.is_login = False
                    return None

                resp = None
                try:
                    resp = func(largs, *args, **kargs)
                except Exception as err:
                    logger.error('Auth Error, %s', err)

                if resp is None:
                    logger.error('Unknown error without response')
                    return None

                if uses_user_token and resp.code == ERR_CODE_TOKEN_EXPIRED:
                    logger.warn('Token expired code=%d, msg=%s', resp.code, resp.msg)
                    largs.user_access_token = auth.refresh_token()
                    continue
                elif resp.code != 0:
                    logger.error('Failed to execute func, code=%d, msg=%s', resp.code, resp.msg)
                    return None

                auth.is_login = True
                return resp.data
            return None

        return inner

    return outer
