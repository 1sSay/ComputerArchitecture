import sys

MEM_SIZE = 1 * 2**20  # given, 1 MB
ADDR_LEN = 20  # log2(MEM_SIZE)
CACHE_SIZE = 4 * 2**10  # given, 4 KB
CACHE_LINE_SIZE = 64  # 2**OFFSET_LEN
CACHE_LINE_COUNT = 64  # CACHE_SIZE / CACHE_LINE_SIZE
CACHE_WAY = 4  # CACHE_LINE_COUNT / CACHE_SETS_COUNT
CACHE_SETS_COUNT = 16  # 2**IDX_LEN
CACHE_TAG_LEN = 10  # ADDR_LEN - IDX_LEN - OFFSET_LEN
CACHE_IDX_LEN = 4  # given
CACHE_OFFSET_LEN = 6  # given

ADDR1_BUS_LEN = 20
ADDR2_BUS_LEN = 20

DATA1_BUS_LEN = 16
DATA2_BUS_LEN = 16

CTR1_BUS_LEN = 3
CTR2_BUS_LEN = 2


def printf(fstring, *args):
    sys.stdout.write(fstring % args)


class CacheLine:
    def __init__(self) -> None:
        self.tag = -1
        self.last_usage = 10**20
        self.bit = 0
        self.status = 'invalid'


class Cache:
    def __init__(self, cache_type):
        self.cache_type = cache_type
        self.cache_lines = list()
        self.set_bits = [0] * CACHE_SETS_COUNT
        for i in range(CACHE_SETS_COUNT):
            self.cache_lines.append([CacheLine() for i in range(CACHE_WAY)])

    def loadLRU(self, tag, index, offset, bits):
        time_spent = 0
        time_spent += 1  # command and addr

        is_hit = False
        for i in range(CACHE_WAY):
            self.cache_lines[index][i].last_usage += 1
            if not is_hit and self.cache_lines[index][i].tag == tag:
                time_spent += 6  # cache hit!
                time_spent += (bits - 1) // DATA1_BUS_LEN + 1  # d1 bus time

                self.cache_lines[index][i].last_usage = 0
                is_hit = True
        if is_hit:
            return time_spent, True

        time_spent += 4  # cache loose

        time_spent += 1  # command to RAM
        time_spent += 100  # RAM response
        time_spent += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1

        j = 0
        for i in range(CACHE_WAY):
            if (
                self.cache_lines[index][j].last_usage
                < self.cache_lines[index][i].last_usage
            ):
                j = i

        if self.cache_lines[index][j].status == 'modified':
            time_spent += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
            time_spent += 100
            time_spent += 1

        self.cache_lines[index][j].last_usage = 0
        self.cache_lines[index][j].tag = tag
        self.cache_lines[index][j].status = 'shared'

        return time_spent, False

    def checkBits(self, index, i):
        if self.cache_lines[index][i].bit == 0:
            self.cache_lines[index][i].bit = 1

            self.set_bits[index] += 1
            if self.set_bits[index] == CACHE_WAY:
                self.set_bits[index] = 1
                for j in range(CACHE_WAY):
                    if i != j:
                        self.cache_lines[index][j].bit = 0

    def loadBitPLRU(self, tag, index, offset, bits):
        time_spent = 0
        time_spent += 1  # command and addr

        for i in range(CACHE_WAY):
            if self.cache_lines[index][i].tag == tag:
                self.checkBits(index, i)

                time_spent += 6  # cache hit!
                time_spent += (bits - 1) // DATA1_BUS_LEN + 1  # d1 bus time

                return time_spent, True

        

        time_spent += 4  # cache loose
        time_spent += 1  # command to RAM
        time_spent += 100  # RAM response
        time_spent += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1

        for i in range(CACHE_WAY):
            if self.cache_lines[index][i].bit == 0:
                if self.cache_lines[index][i].status == 'modified':
                    time_spent += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
                    time_spent += 100
                    time_spent += 1
            
                self.cache_lines[index][i].tag = tag
                self.checkBits(index, i)
                self.cache_lines[index][i].status = 'shared'
                break
        return time_spent, False

    def load(self, addr, bits):
        offset = addr % 2**CACHE_OFFSET_LEN
        index = addr // 2**CACHE_OFFSET_LEN % 2**CACHE_IDX_LEN
        tag = addr // 2 ** (CACHE_OFFSET_LEN + CACHE_IDX_LEN)

        if self.cache_type == "LRU":
            return self.loadLRU(tag, index, offset, bits)
        elif self.cache_type == "Bit-PLRU":
            return self.loadBitPLRU(tag, index, offset, bits)

    def writeLRU(self, tag, index, offset, bits):
        answer = 0

        answer += (bits - 1) // DATA1_BUS_LEN + 1  # d1 bus time

        is_hit = False
        for i in range(CACHE_WAY):
            self.cache_lines[index][i].last_usage += 1
            if not is_hit and self.cache_lines[index][i].tag == tag:
                answer += 6  # cache hit!
                answer += 1  # response
                self.cache_lines[index][i].last_usage = 0
                self.cache_lines[index][i].status = 'modified'
                is_hit = True
        if is_hit:
            return answer, True

        answer += 4  # cache loose

        answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
        answer += 101  # RAM response

        answer += 100
        answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1

        j = 0
        for i in range(CACHE_WAY):
            if (
                self.cache_lines[index][j].last_usage
                < self.cache_lines[index][i].last_usage
            ):
                j = i
        
        if self.cache_lines[index][j].status == 'modified':
            answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
            answer += 100
            answer += 1

        self.cache_lines[index][i].status = 'modified'
        self.cache_lines[index][j].last_usage = 0
        self.cache_lines[index][j].tag = tag
        return answer, False

    def writeBitPLRU(self, tag, index, offset, bits):
        answer = 0

        answer += (bits - 1) // DATA1_BUS_LEN + 1  # d1 bus time
        # answer += 1

        for i in range(CACHE_WAY):
            if self.cache_lines[index][i].tag == tag:
                answer += 6  # cache hit!
                answer += 1  # response
                self.checkBits(index, i)
                self.cache_lines[index][i].status = 'modified'
                return answer, True

        answer += 4  # cache loose
        answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
        answer += 101  # RAM response

        answer += 100
        answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1

        for i in range(CACHE_WAY):
            if self.cache_lines[index][i].bit == 0:
                if self.cache_lines[index][i].status == 'modified':
                    answer += (CACHE_LINE_SIZE * 8 - 1) // DATA2_BUS_LEN + 1
                    answer += 100
                    answer += 1
                self.cache_lines[index][i].status = 'modified'
                self.cache_lines[index][i].tag = tag
                self.checkBits(index, i)
                break
        return answer, False

    def write(self, addr, bits):
        offset = addr % 2**CACHE_OFFSET_LEN
        index = addr // 2**CACHE_OFFSET_LEN % 2**CACHE_IDX_LEN
        tag = addr // 2 ** (CACHE_OFFSET_LEN + CACHE_IDX_LEN)

        if self.cache_type == "LRU":
            return self.writeLRU(tag, index, offset, bits)
        elif self.cache_type == "Bit-PLRU":
            return self.writeBitPLRU(tag, index, offset, bits)


M = 64  # 0 tics
N = 60
K = 32


def calc_program_time(cache_type) -> tuple:
    cache = Cache(cache_type)

    t = 0
    cache_hits = 0
    cache_loses = 0

    t += 1  # pointer init
    pa = int("0x40000", 16)

    t += 1  # pointer init
    pc = int("0x40800", 16)

    t += 1  # y init
    for y in range(M):
        t += 1  # next iteration

        t += 1  # x init
        for x in range(N):
            t += 1  # next iteration

            t += 1  # pointer init
            pb = int("0x41700", 16)

            t += 1  # s init
            s = 0

            t += 1  # k init
            for k in range(K):
                t += 1  # next iteration

                # getting items from cache or memory
                read_time, hit = cache.load(pa, 8)
                t += read_time
                if hit:
                    cache_hits += 1
                else:
                    cache_loses += 1

                read_time, hit = cache.load(pb, 16)
                t += read_time
                if hit:
                    cache_hits += 1
                else:
                    cache_loses += 1

                t += 5  # mul
                t += 1

                pb += N * 2
                t += 1  # add

                t += 1 # increment

            # getting items from cache or memory
            t += 1  # replace
            write_time, hit = cache.write(pc, 32)
            t += write_time
            if hit:
                cache_hits += 1
            else:
                cache_loses += 1

            t += 1 # increment

        pa += K
        t += 1  # add

        pc += N * 4
        t += 1  # add

        t += 1 # increment

    # function exit
    t += 1

    return t, cache_hits, cache_loses


def print_lists_in_memory():
    a_size = M * K
    b_size = 2 * K * N
    c_size = 4 * M * N

    first = int("0x40000", 16)

    def print_mem(s, start, end):
        print(s, hex(start), hex(end))

    print_mem("a:", first, first + a_size - 1)
    print_mem("b:", first + a_size, first + a_size + b_size - 1)
    print_mem("c:", first + a_size + b_size, first + a_size + b_size + c_size - 1)
    print("Total memory:", (a_size + b_size + c_size) / 1024)


t_lru, hits_lru, loses_lru = calc_program_time("LRU")
t_bit_plru, hits_bit_plru, loses_bit_plru = calc_program_time("Bit-PLRU")

hit_rate_lru = hits_lru / (hits_lru + loses_lru) * 100
hit_rate_bit_plru = hits_bit_plru / (hits_bit_plru + loses_bit_plru) * 100
printf(
    "LRU:\thit perc. %3.4f%%\ttime: %d\n" "pLRU:\thit perc. %3.4f%%\ttime: %d\n",
    hit_rate_lru,
    t_lru,
    hit_rate_bit_plru,
    t_bit_plru,
)
