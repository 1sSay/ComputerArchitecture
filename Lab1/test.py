import random
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
            print("Division by zero")
            exit(0)
        
        result = (self.signed << (self.b)) // second.signed
        result &= (1 << (self.a + self.b)) - 1

        return FixedPointNumber(result, self.a, self.b)
    
    def debug(self, number1, number2, res):
        print("Number1:", number1.signed)
        print("Number2:", number2.signed)
        print("Result:", res, bin(res))
    
    def print(self) -> None:
        digit = (self.number >> self.b)

        fraction_bin = self.number & ((1 << self.b) - 1)
        fraction = (fraction_bin * 10 ** 3) >> self.b

        if self.sign:
            digit -= (1 << self.a)
            fraction = (1000 - fraction) % 1000

        if self.sign and fraction != 0:
            digit += 1

        result = ''
        if self.sign:
            result = '-'
        result += str(abs(digit)) + '.' + str(abs(fraction)).zfill(3)

        return result


if __name__ == "__main__":
    error = 0

    for i in range(30):
        a = random.randint(1, 32)
        b = random.randint(0, 32 - a)
        
        number1 = random.randint(0, (1 << (a + b)) - 1)
        number2 = random.randint(0, (1 << (a + b)) - 1)
        if number2 == 0:
            continue
        
        sign1 = number1 >> (a + b - 1)
        sign2 = number2 >> (a + b - 1)
        
        fixed1 = FixedPointNumber(number1, a, b)
        fixed2 = FixedPointNumber(number2, a, b)
        
        float1 = number1 / (1 << b) - sign1 * (1 << (a))
        float2 = number2 / (1 << b) - sign2 * (1 << (a))

        res = (fixed1 / fixed2).print()
        true = float1 / float2
        
        while true >= (1 << (a - 1)):
            true -= (1 << a)
        while true < -(1 << (a - 1)):
            true += (1 << a)
        
        if abs(float(res) - true) >= 1 / min(1 << b, 8):
            error += 1
            print('ERROR')
        
        print(number1)
        print(number2)
        print(a, b)
        print(res)
        print(true)
        print()

    print("Done! Errors count:", error)
