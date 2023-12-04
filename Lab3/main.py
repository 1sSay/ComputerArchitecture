import sys


def printf(format, *args):
    sys.stdout.write(format % args)


MEM_SIZE = 2**20

CACHE_IDX_LEN = 4
CACHE_OFFSET_LEN = 6
CACHE_SIZE = 4 * 2**10



class Cache:
    pass


class Memory:
    def __init__(self) -> None:
        pass


class Processor:
    def __init__(self) -> None:
        pass

    def C1_READ8(self):
        pass

    def C1_READ16(self):
        pass

    def C1_READ32(self):
        pass

    def C1_WRITE8(self):
        pass

    def C1_WRITE16(self):
        pass

    def C1_WRITE32(self):
        pass


if __name__ == "__main__":
    processor = Processor()
    cache = Cache()
    memory = Memory()
