import redis

# Подключение к Redis (используй "redis" как хост в Docker, если код работает внутри контейнера)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Пример: сохранить значение
redis_client.set('my_key', 'Hello Redis!')

# Пример: получить значение
value = redis_client.get('my_key')
print(f'Значение: {value}')
