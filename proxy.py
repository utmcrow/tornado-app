__author__ = 'crow'

import settings
from pymongo.cursor import Cursor
from pymongo import MongoClient
from collections import Mapping

try:
    from settings import DB_HOST, DB_PORT
    DEFAULT_HOST = DB_HOST
    DEFAULT_PORT = DB_PORT
except ImportError:
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 27017

_mongo_clients = {}

def get_mongo_client(host=DEFAULT_HOST, port=DEFAULT_PORT, **kwargs):
    """Return (cached) MongoClient instance for provided URL.

    :param host: Host to connect.
    :type host: basestring
    :param port: Port to connect.
    :type port: int
    :rtype: MongoClient
    :return: Instance of MongoClient for provided host - port pair.
    """
    url = '{}:{}'.format(host, port)
    try:
        return _mongo_clients[(host, port)]
    except KeyError:
        client = _mongo_clients[(host, port)] = MongoClient(host, port, **kwargs)
        return client

class MongoProxy():
    db = ''
    collection = ''
    use_cache = True
    include_fields = ()
    exclude_fields = ()
    dump_fields = ()

    _all = []
    _data_provider = None

    def __init__(self, _id=None, data=None):
        if _id is not None:
            data = self.get_document(_id)
        data = data or {}
        super(MongoProxy, self).__init__(data)

    @classmethod
    def find(cls, *args, **kwargs):
        return cls.get_data_provider().find(*args, **kwargs)

    @classmethod
    def get_data_provider(cls):
        if cls._data_provider is None:
            cls._data_provider = DataProvider(cls.db, cls.collection, cls.use_cache)
        return cls._data_provider

    @classmethod
    def get_document(cls, _id):
        document = cls.get_data_provider().get(
            _id, include_fields=cls.include_fields, exclude_fields=cls.exclude_fields)
        if not document:
            raise KeyError('Document "{}" not found'.format(_id))
        return document

    @classmethod
    def all(cls):
        for data in cls.get_data_provider().find(
                include_fields=cls.include_fields, exclude_fields=cls.exclude_fields):
            yield cls(data=data)

    @classmethod
    def ids(cls):
        return cls.get_data_provider().ids()

    @classmethod
    def get_names(cls):
        """
        Alias for ids
        """
        return cls.ids()

    @property
    def id(self):
        return self['_id']

    @classmethod
    def save(cls, document):
        return cls.get_data_provider().save(document)


class DataProvider(Mapping):
    def _get_collection(self, host, port, db, collection):
        try:
            return self._collection
        except AttributeError:
            self._collection = get_mongo_client(host, port)[db][collection]
            return self._collection

    @property
    def collection(self):
        return self._collection

    _global_cache = {}

    @classmethod
    def _get_cache(cls, db, collection):
        return cls._global_cache.setdefault((db, collection), {})

    _index_ttl = 3600

    def __init__(self, db, collection, use_cache=False, indexes=None, host=settings.DB_HOST, port=settings.DB_PORT):
        self._db_name = db
        self._collection_name = collection
        self._host = host
        self._port = port
        self._collection = self._get_collection(host, port, db, collection)

        if indexes is not None:
            for index_name in indexes:
                self._collection.ensure_index(index_name, ttl=self._index_ttl)

        self._cache = None
        self._init_cache(db, collection, use_cache)

    def _init_cache(self, db, collection, use_cache=False):
        if use_cache:
            self._cache = self._get_cache(db, collection)

    @property
    def cache(self):
        return self._cache

    def drop_cache_entry(self, _id):
        if self.use_cache:
            try:
                del self._cache[_id]
            except KeyError:
                pass

    def _prepare_fields(self, include_fields, exclude_fields):
        if self.use_cache:
            return None
        if include_fields:
            fields = dict.fromkeys(include_fields, 1)
            return fields
        if exclude_fields:
            return dict.fromkeys(exclude_fields, 0)

    @property
    def use_cache(self):
        return self._cache is not None

    def get(self, _id, include_fields=None, exclude_fields=None, force_reload=False):
        """
        Get document from collection by its primary key. 'fields' argument does not matter,
        if DataProvider caches it's data.
        """
        fields = self._prepare_fields(include_fields, exclude_fields)
        if self.use_cache and (not force_reload) and _id in self._cache:
            return self._cache[_id]

        document = self._collection.find_one(_id, fields=fields)
        if self.use_cache:
            if document:
                self._cache[_id] = document
            else:
                self.drop_cache_entry(_id)
        return document

    @staticmethod
    def _keys_iterator(cursor):
        for document in cursor:
            yield document['_id'], document

    def find(self, *args, **kwargs):
        """Searches collection for documents, that matches filters. Cache is ignored for this operation.
        """
        include_fields = kwargs.pop('include_fields', {})
        exclude_fields = kwargs.pop('exclude_fields', {})
        kwargs['fields'] = kwargs.get('fields') or self._prepare_fields(include_fields, exclude_fields)
        keys = kwargs.pop('keys', False)
        cursor = self._collection.find(*args, **kwargs)
        if keys:
            return self._keys_iterator(cursor)
        else:
            return cursor

    def find_and_modify(self, *args, **kwargs):
        """Executes find and modify against the collection.
        """
        return self._collection.find_and_modify(*args, **kwargs)

    def find_one(self, spec, *args, **kwargs):
        include_fields = kwargs.pop('include_fields', {})
        exclude_fields = kwargs.pop('exclude_fields', {})
        kwargs['fields'] = kwargs.get('fields') or self._prepare_fields(include_fields, exclude_fields)
        if not isinstance(spec, dict):
            spec = {'_id': spec}
        return self._collection.find_one(spec, *args, **kwargs)

    def all(self, include_fields=None, exclude_fields=None, keys=False, *args, **kwargs):
        """Return cursor with all documents in collection.

        :rtype: Cursor
        """
        return self.find(include_fields=include_fields, exclude_fields=exclude_fields, keys=keys, *args, **kwargs)

    def ids(self):
        """List ids of all documents in collection
        """
        return self._collection.distinct('_id')

    def save(self, document, safe=False):
        """Saves document in collection. Creates one, if not exists yet.
        """
        self._collection.save(document, safe=safe)
        if hasattr(document, '_id'):
            self.drop_cache_entry(document['_id'])

    def insert(self, documents, **kwargs):
        """Stores documents into the collection.

        :param documents: document or list of documents to store.
        """
        if not isinstance(documents, list):
            documents = [documents]
        self._collection.insert(documents, **kwargs)

    def update(self, spec, update, **kwargs):
        """Updates documents in collection.
        You can also pass named args, supported by pymongo.Collection.update method.
        Warning! Update with query will reset all cached documents for this collection.

        :param spec: id, list of ids or query for documents to update.
        :type spec: dict or list of basestring or tuple of basestring or basestring or bson.ObjectID
        :param update: update specification
        :type update: dict
        """
        if isinstance(spec, dict):
            multi = True
        elif isinstance(spec, (list, set,)):
            multi = True
            spec = {'_id': {'$in': spec}}
        elif isinstance(spec, basestring):
            spec = {'_id': spec}
            multi = False
        else:
            raise TypeError('Invalid query: {}'.format(spec))
        kwargs.setdefault('multi', multi)
        self._collection.update(spec, update, safe=True, **kwargs)

    def remove(self, spec=None):
        if spec is not None:
            if isinstance(spec, basestring):
                self.drop_cache_entry(spec)
                spec = {'_id': spec}
            self._collection.remove(spec)
        else:
            self._collection.remove()
            if self.use_cache:
                self._cache.clear()

    # Mapping implementation
    def __getitem__(self, item):
        return self.get(item)

    def __len__(self):
        return self._collection.count()

    def __iter__(self):
        return self.all()

    def keys(self):
        return self.ids()


class Test(MongoProxy):
    db = settings.DB_DATA
    collection = 'test'
    use_cache = True