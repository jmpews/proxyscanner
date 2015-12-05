# 暂不使用
class LockContext(object):
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, type, value, traceback):
        if type != None:
            pass
        self.lock.release()
        return False