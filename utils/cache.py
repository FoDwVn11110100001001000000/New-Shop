import redis

from utils.logs import log
from env import Config as config


class RedisManager:
    def __init__(
            self, 
            host=config.redis_host, 
            port=config.redis_port, 
            db=0, 
            decode_responses=True
            ):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses
            )

            self.client.ping()
            log.info("✅ Success connection to Redis")
        except redis.ConnectionError as e:
            log.error(f"❌ Error connection to Redis: {e}")
            raise

    def set_value(self, key: str, value: str, expire: int = None) -> None:
        """Устанавливает значение по ключу с необязательным временем жизни"""
        self.client.set(name=key, value=value, ex=expire)

    def get_value(self, key: str) -> str:
        """Получает значение по ключу"""
        return self.client.get(key)

    def delete_key(self, key: str) -> bool:
        """Удаляет ключ"""
        return self.client.delete(key)

    def get_all_keys(self) -> list:
        """Возвращает все ключи в базе"""
        return self.client.keys('*')

    def get_all_data(self) -> dict:
        """Возвращает все ключи и их значения"""
        data = {}
        for key in self.get_all_keys():
            key_type = self.client.type(key)
            if key_type == b'string':
                data[key] = self.client.get(key)
            elif key_type == b'hash':
                data[key] = self.client.hgetall(key)
            elif key_type == b'list':
                data[key] = self.client.lrange(key, 0, -1)
            elif key_type == b'set':
                data[key] = self.client.smembers(key)
            elif key_type == b'zset':
                data[key] = self.client.zrange(key, 0, -1, withscores=True)
            else:
                data[key] = "Unsupported type"
        return data
