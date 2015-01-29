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

    def get_data_provider(self):
        collection = self.settings['db'][self.db][self.collection]
        return collection

    def get_document(self, _id):
        return self.get_data_provider().find_one(_id)

    def find(self, *args, **kwargs):
        return self.get_data_provider().find(*args, **kwargs)

