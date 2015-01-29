__author__ = 'crow'

import tornado.ioloop
import tornado.web
import tornado.httpserver
import routes
import settings
import os.path
import motor

try:
    from settings import DB_HOST, DB_PORT
    DEFAULT_HOST = DB_HOST
    DEFAULT_PORT = DB_PORT
except ImportError:
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 27017


class Application(tornado.web.Application):
    def __init__(self):
        handlers = routes.routes
        options = dict(
            cookie_secret=settings.COOKIE_SECRET,
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=settings.DEBUG,
            db=motor.MotorClient(DEFAULT_HOST, DEFAULT_PORT)
        )
        tornado.web.Application.__init__(self, handlers, **options)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()