__author__ = 'crow'

import tornado.web
import tornado.escape
import tornado.auth
import settings

from tornado import gen

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie(settings.COOKIE_TOKEN)
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("main.html")

class PageHandler(BaseHandler):
    def get(self):
        self.write("Hello, page")

class ExampleHandler(BaseHandler):
    def get(self):
        self.render("example.html")

class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            user = yield self.get_authenticated_user()
            self.set_secure_cookie(settings.COOKIE_TOKEN,
                                   tornado.escape.json_encode(user))
            self.redirect("/example")
            return
        self.authenticate_redirect(ax_attrs=["name"])


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(settings.COOKIE_TOKEN)
        self.write("You are now logged out")