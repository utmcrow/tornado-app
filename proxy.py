__author__ = 'crow'


import settings
from db.pymongo.proxy import MongoProxy

class PymongoTestProxy(MongoProxy):
    db = settings.DB_DATA
    collection = 'test'
    use_cache = True