__author__ = 'crow'

import handlers

routes = [
    (r"/", handlers.MainHandler),
    (r"/page", handlers.PageHandler),
    (r"/pymongotestget-([^/]+)", handlers.PymongoTestHandlerGet),
    (r"/pymongotestset-([^/]+)", handlers.PymongoTestHandlerSet),
    (r"/auth/login", handlers.AuthLoginHandler),
    (r"/auth/logout", handlers.AuthLogoutHandler),
]