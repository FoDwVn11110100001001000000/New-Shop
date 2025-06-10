import json
import redis.asyncio as redis
from utils.logs import log
from env import Config as config


class RedisManager:
    def __init__(
        self,
        host=config.redis_host,
        port=config.redis_port,
        expire=config.redis_expire,
        db=0,
        decode_responses=True
    ):
        """
        Constructor for RedisManager class.

        Args:
            host (str): Redis host. Defaults to config.redis_host.
            port (int): Redis port. Defaults to config.redis_port.
            expire (int): Expiration time in seconds. Defaults to config.redis_expire.
            db (int, optional): Redis database number. Defaults to 0.
            decode_responses (bool, optional): If True, all responses will be decoded with utf-8. Defaults to True.
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )
        self.expire = expire

    async def connect(self):
        """
        Checks the connection to Redis.

        Tries to ping Redis server and log the result.
        If the connection fails, logs an error and raises the exception.
        """
        try:
            await self.client.ping()
            log.info("✅ Success connection to Redis")
        except redis.ConnectionError as e:
            log.error(f"❌ Error connection to Redis: {e}")
            raise

    async def reserve_lots(self, telegram_id: int, lots: list[dict]) -> None:
        """
        Reserves lots for a given telegram_id.

        Args:
            telegram_id (int): Telegram user ID.
            lots (list[dict]): List of dictionaries with lot data.

        Returns:
            None
        """
        value = json.dumps(lots)
        await self.client.set(name=telegram_id, value=value, ex=self.expire)
        log.info(f"ID: {telegram_id}| Reserved lots: {value}")


    async def get_reserved_by_user(self, telegram_id: int) -> list[dict]:
        """
        Retrieves all reserved lots for a given telegram_id.

        Args:
            telegram_id (int): Telegram user ID.

        Returns:
            list[dict]: List of dictionaries with lot data if found, else an empty list.
        """
        raw = await self.client.get(telegram_id)
        if raw:
            log.info(f"ID: {telegram_id}| Get reserved lots by user: {raw}")
            return json.loads(raw)
        return []

    async def get_all_reserved_by_types(self, telegram_id: str, type: str) -> list[str]:
        """
        Retrieves all reserved lots for a given telegram_id and type.

        Args:
            telegram_id (str): Telegram user ID.
            type (str): Type of the lot to retrieve.

        Returns:
            list[str]: List of strings with the type of the lot for the given
                telegram_id and type if found, else an empty list.
        """

        keys = await self.client.keys(f"{telegram_id}")
        types = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                lots = json.loads(raw)
                types.extend({type: lot[type]} for lot in lots if type in lot)
        return types

    async def get_all_reserved_types(self, telegram_id: str) -> list[dict[str, str]]:
        """
        Retrieves all reserved lot types for a given telegram_id.

        Args:
            telegram_id (str): Telegram user ID.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing lot type data
            associated with the given telegram_id. If no data is found, returns an
            empty list.
        """
        keys = await self.client.keys(f"{telegram_id}")
        types = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                lots = json.loads(raw)
                types.extend(lots)
        return types
