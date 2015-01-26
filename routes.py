__author__ = 'crow'

import handlers

routes = [
    (r"/", handlers.MainHandler),
    (r"/page", handlers.PageHandler),
    (r"/mongotestget-([^/]+)", handlers.MongoTestHandlerGet),
    (r"/mongotestset-([^/]+)", handlers.MongoTestHandlerSet),
    (r"/auth/login", handlers.AuthLoginHandler),
    (r"/auth/logout", handlers.AuthLogoutHandler),
]