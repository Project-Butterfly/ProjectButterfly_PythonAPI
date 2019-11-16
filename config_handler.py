import json
import logging
import os
from configparser import ConfigParser

SINGLETON = None


class ConfigHandler:
    def __init__(self, db_config_file='./credentials/db_credentials.ini', db_config_section='postgresql',
                 users_config='./credentials/users.json'):
        self.db_config_file = db_config_file
        self.db_config_section = db_config_section
        self.users_config = users_config

        if not os.path.isfile(users_config):
            try:
                with open(users_config, "a+") as users_config:
                    users_config.write("{}")
            except IOError as e:
                logging.error("Unable to create given UserConfig File", e)

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

    def get_user_configs(self) -> dict:
        with open(self.users_config, "r") as config_file:
            return json.load(config_file)

    def insert_user_config(self, phone_number, password):
        with open(self.users_config, "r") as config_file:
            config = json.load(config_file)
            config[phone_number] = password
        with open(self.users_config, "w") as config_file:
            json.dump(config, config_file, indent=2)


def get_default():
    global SINGLETON
    if SINGLETON is None:
        SINGLETON = ConfigHandler()
    return SINGLETON
