__author__ = 'crow'

import handlers

routes = [
    (r"/", handlers.MainHandler),
    (r"/page", handlers.PageHandler),
    (r"/example", handlers.ExampleHandler),
    (r"/auth/login", handlers.AuthLoginHandler),
    (r"/auth/logout", handlers.AuthLogoutHandler),
]