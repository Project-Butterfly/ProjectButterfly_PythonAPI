import json
from configparser import ConfigParser


SINGLETON = None


class ConfigHandler:
    def __init__(self, db_config_file='db_credentials.ini', db_config_section='postgresql'):
        self.db_config_file = db_config_file
        self.db_config_section = db_config_section

    def get_db_config(self):
        parser = ConfigParser()
        parser.read(self.db_config_file)

        config = {}
        if parser.has_section(self.db_config_section):
            for param in parser.items(self.db_config_section):
                config[param[0]] = param[1]
        else:
            raise Exception("Section %s not found in '%s'" % (self.db_config_section, self.db_config_file))

        return config


def get_default():
    global SINGLETON
    if SINGLETON is None:
        SINGLETON = ConfigHandler()
    return SINGLETON
