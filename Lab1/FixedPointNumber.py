from typing import Self


class FixedPointNumber:
    def __init__(self, number: int, a: int, b: int) -> None:
        self.a = a
        self.b = b
        self.number = number
        self.sign = self.number >> (self.a + self.b - 1)
        self.signed = self.number - self.sign * (1 << (self.a + self.b))

    def __add__(self, second: Self) -> Self:
        result = (self.number + second.number) % (1 << (self.a + self.b))
        return FixedPointNumber(result, self.a, self.b)

    def __sub__(self, second: Self) -> Self:
        result = (self.number + (~second.number + 1)) % (1 << (self.a + self.b))
        return FixedPointNumber(result, self.a, self.b)

    def __mul__(self, second: Self) -> Self:
        result = self.signed * second.signed
        result >>= self.b
        result &= (1 << (self.a + self.b)) - 1

        return FixedPointNumber(result, self.a, self.b)

    def __truediv__(self, second: Self) -> Self:
        if second.number == 0:
            print("error")
            exit(0)

        result = (self.signed << (self.b)) // second.signed
        result &= (1 << (self.a + self.b)) - 1

        return FixedPointNumber(result, self.a, self.b)

    def print(self) -> None:
        digit = (self.number >> self.b)

        fraction_bin = self.number & ((1 << self.b) - 1)
        fraction = (fraction_bin * 10 ** 3) >> self.b

        if self.sign:
            fraction = (1000 - fraction) % 1000

            digit -= (1 << self.a)
            if fraction != 0:
                digit += 1

        result = ''
        if self.sign:
            result = '-'
        result += str(abs(digit)) + '.' + str(abs(fraction)).zfill(3)

        return result