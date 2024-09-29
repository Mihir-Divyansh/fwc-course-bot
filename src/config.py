import pandas as pd
import src.serializers as serializers
from pathlib import Path as path

# Handles error when getting settings by key
class Config:
    def __init__(self, secretsJsonFile : str):
        self.secrets_file = secretsJsonFile
        self.secrets : serializers.SerializedJSON = serializers.SerializedJSON(secretsJsonFile)

        self.config_file = self.secrets['config']
        self.__config : serializers.SerializedJSON = serializers.SerializedJSON(self.config_file)

        self.discord_token = self.secrets['discord-api-token']

    def get(self, key : str) -> dict | str | float | bool | None:
        return self.__config.get(key=key)
    def getstr(self, key : str) -> str:
        return self.__config.getstr(key=key)
    def getstrlower(self, key : str) -> str:
        return self.__config.getstrlower(key=key)
    
    def get_role(self, roleID : int) -> str | None:
        roles = self.get('roles')
        # print(roles)
        # go through all roles
        for key, value in roles.items():
            if value['id'] == roleID:
                return value['name']
        return None

    def isRoleChannelDM(self, roleID : int) -> str | None:
        roles = self.get('roles')
        # go through all roles
        for key, value in roles.items():
            if value['id'] == roleID:
                return value['dm-channels']
        return None

    def __getitem__(self, key):
        return self.__config[key]
