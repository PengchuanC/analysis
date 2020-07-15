import os
import shelve


base_dir = os.path.dirname(__file__)


class DataBase(object):
    def __init__(self):
        self.path = os.path.join(base_dir, "dataset")

    def dump(self, name, data):
        with shelve.open(self.path) as s:
            if name in s.keys():
                raise KeyError(f"keyword `name` exists in database\nyou may use method <update>")
            s[name] = data

    def load(self, name):
        with shelve.open(self.path) as s:
            ret = s.get(name, None)
        return ret

    def delete(self, name):
        with shelve.open(self.path) as s:
            del s[name]
        print(f"`{name}` removed from database")

    def update(self, name, data):
        with shelve.open(self.path) as s:
            if name not in s.keys():
                raise KeyError(f"keyword `name` not exist in database\nyou may use method <dump>")
            s[name] = data

    def preview(self):
        with shelve.open(self.path) as s:
            keys = list(s.keys())
        print(keys)
        return keys
