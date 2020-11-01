"""
A general-purpose LRU cache.
"""

from collections import OrderedDict


class LRUCache:

    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        """Returns the item in the cache by key.

        :param key: the key of the item to return.
        :return: item stored in the cash with key `key`.
        """
        if key not in self.cache:
            return None
        else:
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value):
        """Adds a value to the cache, evicting the least-
        recently used item if the cache is at capacity.

        :param key: the key to store the new item under.
        :param value: the value to store for key.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
