import json
import os


class CountryNameMatcher:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(dir_path + '/keys_to_names.json') as file:
            keys_to_names = json.load(file)
        names_to_keys = {
            name.lower(): key
            for key, name in keys_to_names.items()}
        with open(dir_path + '/names_to_keys.json') as file:
            names_to_keys = {**json.load(file), **names_to_keys}
        self._keys_to_names = DictLeavingMissings(keys_to_names)
        self._names_to_keys = DictLeavingMissings(names_to_keys)

    def name_to_key(self, name=None):
        if name is None:
            return self._names_to_keys
        name = name.lower()
        return self._names_to_keys[name]

    def key_to_name(self, key=None):
        if key is None:
            return self._keys_to_names
        return self._keys_to_names[key]

    def keys(self):
        return set(self._keys_to_names.keys())


class DictLeavingMissings(dict):
    def __missing__(self, key):
        return key
