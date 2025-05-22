from pymongo                import MongoClient
from optalim.settings       import TESTING, MONGO_HOST, MONGO_PORT
from mock                   import MagicMock

class Mongo(object):
    if TESTING:
        client = None
    else:
        client = MongoClient(MONGO_HOST, MONGO_PORT, connect=False)

    @classmethod
    def log_table(cls, name):
        if TESTING:
            return MagicMock()
        return cls.client["logs"][name]

    @classmethod
    def hp_table(cls, name):
        if TESTING:
            return MagicMock()
        return cls.client["hippocrate"][name]
