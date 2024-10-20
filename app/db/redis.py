import redis

r = redis.Redis(host='localhost', port=6379, db=6, decode_responses=True)
