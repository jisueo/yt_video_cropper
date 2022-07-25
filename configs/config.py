import json
import os

"""Clss Configs environment config value provider

    Configs provide environment values like db scheme, file path, const values
    if value from file that ./secrets.json or os env(export DB=mysql:127.0.0.1)

    Typical usage example:

    config = Configs()ß
    credential = config.get_attr('CREDENTIAL')

    credential = Configs.instance().get_attr('CREDENTIAL')
"""
class Configs:
    
    __BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    __JSON_OBJ = None
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance

    def __init__(self, **kwargs):
        if self.__JSON_OBJ == None:
            self.__try_load_secrets_json()

    def __try_load_secrets_json(self, **kwargs):
        try:
            config_file_path = self.__BASE_DIR + "/secrets.json"
            with open(config_file_path) as f:
                self.__JSON_OBJ = json.loads(f.read())

        except FileNotFoundError:
            error_msg = "Not found file in ({0})".format(
                self.__BASE_DIR + "/secrets.json"
            )
            print(error_msg)
            print("no secrets file, os environment mode is activated")
            self.__JSON_OBJ = None

    def get_attr(self, attr: str):
        try:
            if self.__JSON_OBJ:
                return self.__JSON_OBJ.get(attr, None)
            else:
                return os.environ.get(str)
        except KeyError:
            error_msg = "Not found {0} in environment variable".format(attr)
            raise FileNotFoundError(error_msg)

    @property
    def get_json(self):
        return self.__JSON_OBJ
