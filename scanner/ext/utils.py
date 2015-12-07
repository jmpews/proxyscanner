import threading
MyLock = threading.RLock()
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


def int2byte(x):
    if x<255:
        return [chr(x)]
    a=chr(x&0xFF)
    b=x>>8
    return ''.join([a]+int2byte(b))

# print(int2byte(443))

def byte2hex(x):
    return ''.join(['%02X' % ord(x) for x in x]).strip()

def SSEncryptor(key):
    from ext.shadowsocks import encrypt
    key=key.encode()
    encryptor = encrypt.Encryptor(key, 'aes-256-cfb')
    # encryptor = encrypt.Encryptor(b'password', 'aes-256-cfb')
    return encryptor

def ip2n(str):
    i = [int(x) for x in str.split('.')]
    return i[0] << 24 | i[1] << 16 | i[2] << 8 | i[3]

def n2ip(num):
    return '%s.%s.%s.%s' % (
        (num & 0xFF000000) >> 24,
        (num & 0x00FF0000) >> 16,
        (num & 0x0000FF00) >> 8,
        (num & 0x000000FF)
    )
