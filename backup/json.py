import json
from pathlib import Path


class JsonMemory:
    """
    Simple Json key pair database
    """

    def __init__(self, location):
        """
        :param location: storage location
        """

        if type(location) != Path:
            self.location = Path(location)
        else:
            self.location = location

        self.location.parent.mkdir(parents=True, exist_ok=True)

        self.data = {}

        self.load()

    def load(self):
        """
        load from storage to memory
        """
        try:
            with self.location.open('r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.save()

    def save(self):
        """
        save current memory to storage
        """
        with self.location.open('w') as f:
            json.dump(self.data, f)

    def get(self, key, default=None):
        """
        :param key: key used as identifier
        :param default: value to return is key not found

        :return: data corresponding to identifer(key)
        :returns: default if key not found
        """
        try:
            value = self.data[key]
        except KeyError:
            value = default

        return value

    def delete(self, key):
        """
        removes the key from memory

        :param key: key to be removed
        """
        try:
            del self.data[key]
        except KeyError:
            pass

    def put(self, key, value):
        """
        adds key-value pair to memory

        :param key: key used as identifier
        :param value: data to store
        """
        self.data[key] = value

    def putall(self, map: dict):
        """
        adds all the key-value pairs in the map

        :param map: dictionary map to be stored
        """
        for key, value in map.items():
            self.data[key] = value