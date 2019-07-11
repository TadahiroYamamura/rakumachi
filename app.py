import redis

from rakumachi import Rakumachi


class DataStore:
    def __init__(self):
        self.store = redis.Redis()

    def exists(self, hash):
        return self.store.exists(hash) != 0

    def register_company(hash, name, data):
        self.store.hset(hash, "name", name)
        self.store.hset(hash, "data", "\t".join(data))


def main(debug):
    Rakumachi(DataStore(), debug=False).with_credential(
        "mt.village12@gmail.com",
        "jAGYLqGMBo"
    ).search({"area": [13]})


if __name__ == "__main__":
    main(False)
