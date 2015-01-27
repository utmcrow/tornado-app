__author__ = 'crow'


import settings
from db.pymongo.proxy import PymongoProxy
from db.motor.proxy import MotorProxy

class PymongoTestProxy(PymongoProxy):
    db = settings.DB_DATA
    collection = 'test'
    use_cache = True


class MotorTestProxy(MotorProxy):
    db = settings.DB_DATA
    collection = 'test'
    use_cache = True