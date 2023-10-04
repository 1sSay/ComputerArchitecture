import sys
from typing import Self

ROUND_METHOD = "3"


class FloatingPointNumber:
    def __init__(self, number: int, size: int) -> None:
        self.size = size
        self.number = number

        if size == 16:
            self.mantissa_bits = 11
            self.exp_bits = 5
        elif size == 32:
            self.mantissa_bits = 24
            self.exp_bits = 8
        
        self.sign = number >> (size - 1)
        self.mantissa = (1 << (self.exp_bits - 1)) + (number & ((1 << (self.exp_bits - 1)) - 1))
        self.exp = ((number >> (self.mantissa_bits - 1)) & ((1 << self.exp_bits) - 1)) - (1 << (self.exp_bits - 1)) + 1
        
    def print(self):
        if self.exp >= 0:
            str_exp = '+' + str(self.exp)
        else:
            str_exp = str(self.exp)
        
        print(bin(self.mantissa))
        
        print('0x1.' + '' + 'p' + str_exp)


class FixedPointNumber:
    def __init__(self, number: int, a: int, b: int) -> None:
        self.a = a
        self.b = b    
        self.number = number
    
    def __add__(self, second: Self) -> Self:
        result = (self.number + second.number) % (2 ** (self.a + self.b))
        
        return FixedPointNumber(result, self.a, self.b)
        
    
    def __sub__(self, second: Self) -> Self:
        result = self.number - second.number
        
        if result < 0:
            result += 2 ** (self.a + self.b) - 1
        
        return FixedPointNumber(result, self.a, self.b)
    
    def __mul__(self, second: Self) -> Self:
        result = self.number * second.number
        result >>= self.b
        result &= (1 << (self.a + self.b + 1)) - 1
        
        return FixedPointNumber(result, self.a, self.b)
    
    def __truediv__(self, second: Self) -> Self:
        result = self.number
        result <<= self.b
        resurt //= second.number
        
        return FixedPointNumber(result, self.a, self.b)
    
    def print(self) -> None:
        sign = self.number >> (self.a + self.b - 1)
        digit = (self.number >> self.b) & (2 ** (1 << (self.a - 1)) - 1)
        fraction_bin = self.number & ((1 << self.b) - 1)
        
        if sign:
            digit -= (1 << self.a)
            fraction_bin = fraction_bin - (1 << self.b)
    
        fraction = fraction_bin * 10 ** 3 // 2 ** self.b
        if sign and fraction != 0:
            digit += 1
        
        print(str(digit) + '.' + str(abs(fraction)))


def check_input(number_type: str, round_method: str, number1: str, operation: str, number2: str):
    errors = list()
    
    def is_fixed_point(number_type):
        if number_type.count('.') == 1:
            a, b = number_type.split('.')
            if a.isdigit() and b.isdigit() and \
                    int(a) > 0 and int(a) + int(b) <= 32:
                return True
        return False
    
    def check_number(number):
        if number is None:
            return
        
        if not number.startswith('0x'):
            errors.append('Wrong input number (Should start with 0x)')
            return
        
        try:
            int(number[2:], 16)
        except ValueError:
            errors.append('Wrong input number (Not in hex)')
            return
        
        if (number_type == 'h' and int(number[2:], 16) >= 2 ** 16) or \
           (number_type == 'f' and int(number[2:], 16) >= 2 ** 64) or \
           (number_type == is_fixed_point(number_type) and \
                int(number_type[2:], 16) >= 2 ** sum([int(i) for i in number_type.split('.')])):
            errors.append('Too big number')
            return


    # Checking number type
    if not (number_type == 'h' or \
           number_type == 'f' or \
           is_fixed_point(number_type)):
        errors.append("Invalid number type")

    # Checking round method
    if round_method != ROUND_METHOD:
        errors.append("Wrong round method. Can only process"
                      "round toward negative infinity (3)")

    # Checking operation
    if not (operation is None or operation in '+-*/'):
        errors.append("Wrong operation. Use +, -, * or /")

    # Checking numbers
    check_number(number1)
    check_number(number2)
    
    return errors


def to_class(number, number_type):
    number = int(number[2:], 16)
    if number_type == 'h':
        return FloatingPointNumber(number, 16)
    elif number_type == 'f':
        return FloatingPointNumber(number, 32)
    else:
        a, b = map(int, number_type.split('.'))
        return FixedPointNumber(number, a, b)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 3 and len(args) != 5:
        print("Wrong arguments count (need 3 or 5)")
        exit(0)
    
    if len(args) == 3:
        args = args + [None, None]
    
    number_type = args[0]
    round_method = args[1]
    number1 = args[2]
    operation = args[3]
    number2 = args[4]
    
    errors = check_input(number_type, round_method, number1, operation, number2)
    if len(errors):
        print(*errors, sep='\n')
        exit(0)
    
    number1 = to_class(number1, number_type)
    result = number1
    
    if operation is not None:
        number2 = to_class(number2, number_type)
        
        if operation == '+':
            result = number1 + number2
        elif operation == '-':
            result = number1 - number2
        elif operation == '*':
            result = number1 * number2
        else:
            result = number1 / number2
    
    result.print()
