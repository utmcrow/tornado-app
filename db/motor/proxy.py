__author__ = 'crow'

import settings
import motor

try:
    from settings import DB_HOST, DB_PORT
    DEFAULT_HOST = DB_HOST
    DEFAULT_PORT = DB_PORT
except ImportError:
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 27017


class MotorProxy():
    db = ''
    collection = ''
    use_cache = True

    @classmethod
    def get_data_provider(cls):
        client = motor.MotorClient(DEFAULT_HOST, DEFAULT_PORT)
        db = client[cls.db]
        collection = db[cls.collection]
        return collection


    @classmethod
    def get_document(cls, _id):
        document = yield cls.get_data_provider().find().count()
        print document
        pass
