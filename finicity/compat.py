try:
    from django.core.cache import cache
except ImportError:
    import time
    from collections import defaultdict
    class Cache(object):
        # {key: {value: "", expiry: unixtimestamp}}
        storage = defaultdict(None)

        def set(self, key, value, timeout=24*60*60):
            Cache.storage[key] = dict(value=value,
                                      expiry=int(time.time()) + timeout)

        def get(self, key, default=None):
            result = Cache.storage.get(key)
            if result is None:
                return default
            else:
                if result['expiry'] < int(time.time()):
                    self.delete(key)
                    return default
                else:
                    return result['value']

        def delete(self, key):
            del Cache.storage[key]
    cache = Cache()