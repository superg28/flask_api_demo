from pymongo import MongoClient, errors
import inspect

# get env variables for the database
from envparse import Env

env = Env(
    MongoUrl=str,
    MongoUser=str,
    MongoPass=str,
    MongoDatabase=str
)

env.read_envfile()

class Singleton(type):
    """ Simple Singleton that keep only one value for all instances
    """
    def __init__(cls, name, bases, dic):
        super(Singleton, cls).__init__(name, bases, dic)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class SingletonArgs(type):
    """ Singleton that keep single instance for single set of arguments. E.g.:
    assert SingletonArgs('spam') is not SingletonArgs('eggs')
    assert SingletonArgs('spam') is SingletonArgs('spam')
    """
    _instances = {}
    _init = {}

    def __init__(cls, name, bases, dct):
        cls._init[cls] = dct.get('__init__', None)

    def __call__(cls, *args, **kwargs):
        init = cls._init[cls]
        if init is not None:
            key = (cls, frozenset(
                    inspect.getcallargs(init, None, *args, **kwargs).items()))
        else:
            key = cls

        if key not in cls._instances:
            cls._instances[key] = super(SingletonArgs, cls).__call__(*args, **kwargs)
        return cls._instances[key]


class MongoDB(object):
    """ Class based on Singleton type to work with MongoDB connections
    """
    __metaclass__ = SingletonArgs

    def __init__(self, url, user, password, db_name=None):
        if db_name:
            self.connection = MongoClient(url, username=user, password=password)[db_name]
        else:
            self.connection = MongoClient(url, username=user, password=password).get_default_database()

    def connection(self):
        return self.connection


def db_init(db_name=None):
    url = 'mongodb://vbox-server:27017/'
    # c = MongoDB(env.str('MongoUrl'), env.str('MongoUser'), env.str('MongoPass'), env.str('MongoDatabase')).connection
    c = MongoDB(env.str('MongoUrl'), env.str('MongoUser'), env.str('MongoPass'), env.str('MongoDatabase')).connection
    return c