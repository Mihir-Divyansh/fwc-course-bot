import json

# Makes accessing nested dicts easy
# For example instead of dict['a']['b']
# you can do: dict['a/b']
class DictTree:
    def __init__(self, dictionary) -> None:
        self.dictionary = dictionary
        self.file = dictionary

    # check if a key exists
    def exists(self, key : str) -> bool:
        setting_list = key.split('/')

        # if setting id ends with '/'
        # ignore it
        if len(setting_list[-1]) == 0:
            setting_list.pop()

        config = self.dictionary
        for key in setting_list:
            if key in config:
                config = config[key]
            else:
                return False

        return True

    # if the key is not found return None
    def get(self, key : str) -> dict | str | float | bool | None:
        setting_list = key.split('/')

        # if setting id ends with '/'
        # ignore it
        if len(setting_list[-1]) == 0:
            setting_list.pop()

        config = self.dictionary
        for key in setting_list:
            if key in config:
                config = config[key]
            else:
                return None

        return config

        # if the key is not found return None

    # convert the value to str and lower it
    # if the key does not exit return empty str
    def getstr(self, key : str) -> str:
        item = self.get(key=key)
        if item:
            return str(item)
        else:
            return ''

    # if the key does not exit return empty str
    # convert the value to str and lower it
    def getstrlower(self, key : str) -> str:
        item = self.get(key=key)
        if item:
            return str(item).lower()
        else:
            return ''

    # get an item, throws exception if key not found
    def __getitem__(self, key : str) -> dict | str | float | bool:
        item = self.get(key=key)
        if not item is None:
            return item
        else:
            raise Exception(f'Fatal Error: {key} is not defined in {self.file}')

    # returns True if the dictTree is empty
    def empty(self) -> bool:
        return len(self.dictionary) == 0

class SerializedDict(DictTree):
    def __init__(self, dictionary) -> None:
        DictTree.__init__(self, dictionary=dictionary)

    # if the key does not exit return None
    def getreader(self, key : str):
        item = self.get(key=key)
        if not item is None:
            return SerializedDict(dict(item))
        else:
            return None

class SerializedJSON(DictTree):
    def __init__(self, json_file : str = '', json_str : str = '', json_dict=None) -> None:
        self.file = json_file
        if json_file:
            with open(json_file, 'r') as f:
                DictTree.__init__(self, dictionary=json.load(f))
            return

        # otherwise load from string
        if json_str:
            DictTree.__init__(self, dictionary=json.loads(json_str))
            return
        
        # otherwise load from dict
        if json_dict:
            DictTree.__init__(self, dictionary=json_dict)
            return

        # otherwise initialize a empty dict
        DictTree.__init__(self, dictionary={})

    # if the key does not exit return None
    def getreader(self, key : str) -> SerializedDict | None:
        item = self.get(key=key)
        if item:
            return SerializedDict(dict(item))
        else:
            return None

    def dumps(self):
        return json.dumps(self.dictionary)

def adapt_sjson(sjson):
    return sjson.dumps()

def converter_sjson(value):
    return SerializedJSON(json_str=value.decode('utf-8'))
