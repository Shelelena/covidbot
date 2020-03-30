import json
import os


class Dictionary:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/keys_to_names.json') as file:
            self._keys_to_names = json.load(file)
        with open(dir_path + '/names_to_keys.json') as file:
            self._names_to_keys = json.load(file)

    def name_to_key(self, name):
        name = name.lower()
        if name in self._names_to_keys:
            return self._names_to_keys[name]
        else:
            return name

    def key_to_name(self, key):
        if key in self._keys_to_names:
            return self._keys_to_names[key]
        else:
            return key

    def key_to_link(self, key):
        return r'/country\_' + key
