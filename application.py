__author__ = 'crow'

import tornado.ioloop
import tornado.web
import routes
import settings
import os.path

from tornado.options import parse_command_line

application = tornado.web.Application(routes.routes)

def main():
    parse_command_line()
    app = tornado.web.Application(
        routes.routes,
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        debug=settings.DEBUG,
        )
    app.listen(settings.PORT)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()