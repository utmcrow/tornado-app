__author__ = 'crow'

import tornado.web
import tornado.escape
import tornado.auth
import settings

from tornado import gen
from proxy import PymongoTestProxy, MotorTestProxy



class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie(settings.COOKIE_TOKEN)
        if not user_json: return None
        return tornado.escape.json_decode(user_json)


class MotorTestHandlerGet(MotorTestProxy, BaseHandler):

    @gen.coroutine
    def get(self, id):
        result = yield self.get_document(id)
        self.render("get.html", entry=result)


class MotorTestHandlerFind(MotorTestProxy, BaseHandler):

    @gen.coroutine
    def get(self):
        result = []
        query = self.find()
        while (yield query.fetch_next):
            result.append(query.next_object())
        pass
        #self.render("get.html", entry=result)


class PymongoTestHandlerGet(BaseHandler):
    def get(self, id):
        testdata = PymongoTestProxy.get_document(id)
        self.render("get.html",entry=testdata)


class PymongoTestHandlerSet(BaseHandler):
    def get(self, id):
        document = {
            '_id': id,
            'data': 'hehe'
        }
        PymongoTestProxy.save(document)


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("example_bootstrap.html")


class PageHandler(BaseHandler):
    def get(self):
        self.render("get.html",entry=False)


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            user = yield self.get_authenticated_user()
            self.set_secure_cookie(settings.COOKIE_TOKEN,
                                   tornado.escape.json_encode(user))
            self.redirect("/")
            return
        self.authenticate_redirect(ax_attrs=["name"])


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(settings.COOKIE_TOKEN)
        self.write("You are now logged out")