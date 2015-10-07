__author__ = 'jmpews'
import redis

class RedisQueue(object):
    def __init__(self,name,**redis_kwargs):
        self.__db=redis.StrictRedis(host='linevery.com', port=6379, db=0)
        self.key = '%s:%s' % (name,namespace)

    def qsize(self):
        return self.__db.llen(self.key)

    def qrange(self,start,end):
        return self.__db.lrange(self.key,start,end)

    def empty(self):
        return self.qsize()==0

    def put(self,item):
        self.__db.rpush(self.key,item)

    def get(self,block=True,timeout=None):
        if block:
            item=self.__db.blpop(self.key,timeout=timeout)
            item=item[1]
        else:
            item=self.__db.lpop(self.key)

        # item=item[1]
        return item

    def get_notwait(self):
        return self.get(block=False)

    def clear(self):
        return self.__db.delete(self.key)