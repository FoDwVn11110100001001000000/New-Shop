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
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )
        self.expire = expire

    async def connect(self):
        try:
            await self.client.ping()
            log.info("✅ Success connection to Redis")
        except redis.ConnectionError as e:
            log.error(f"❌ Error connection to Redis: {e}")
            raise

    async def reserve_lots(self, telegram_id: int, lots: list[dict]) -> None:
        value = json.dumps(lots)
        await self.client.set(name=telegram_id, value=value, ex=self.expire)
        log.info(f"ID: {telegram_id}| Reserved lots: {value}")


    async def get_reserved_by_user(self, telegram_id: int) -> list[dict]:
        """Получает список зарезервированных лотов по telegram_id"""
        raw = await self.client.get(telegram_id)
        if raw:
            log.info(f"ID: {telegram_id}| Get reserved lots by user: {raw}")
            return json.loads(raw)
        return []

    async def get_all_reserved_by_types(self, telegram_id: str, type: str) -> list[str]:
        """Получает все type из всех зарезервированных лотов"""
        keys = await self.client.keys(f"{telegram_id}")
        types = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                lots = json.loads(raw)
                types.extend({type: lot[type]} for lot in lots if type in lot)
        return types

    async def get_all_reserved_types(self, telegram_id: str) -> list[dict[str, str]]:
        """Получает все зарезервированные лоты (список словарей) по telegram_id"""
        keys = await self.client.keys(f"{telegram_id}")
        types = []
        for key in keys:
            raw = await self.client.get(key)
            if raw:
                lots = json.loads(raw)
                types.extend(lots)
        return types
