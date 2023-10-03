import sys

ROUND_METHOD = "3"


class FloatingPointNumber:
    def __init__(self, size, number) -> None:
        self.size = size


class FixedPointNumber:
    def __init__(self, a: int, b: int, number: str) -> None:
        self.a = a
        self.b = b    
        self.number = number + [0] * (a + b - len(number))
    
    def __add__(self, second):
        result = [0] * (self.a + self.b)
        carry = 0
        
        for i in range(self.a + self.b):
            result[i] = (self.number[i] + second.number[i] + carry) % 2
            carry = (self.number[i] + second.number[i] + carry) // 2
        
        return FixedPointNumber(self.a, self.b, result)
    
    def __sub__(self, second):
        result = [0] * (self.a + self.b)
        
        return result
    
    def __mul__(self, second):
        result = [0] * (self.a + self.b)
        
        return result
    
    def __truediv__(self, second):
        result = [0] * (self.a + self.b)
        
        return result
    
    def print(self) -> None:
        is_negative = self.number[-1]
        digit_part = list(reversed(self.number[self.b:-1]))
        fraction_part = list(reversed(self.number[:self.b]))
        
        digit = sum([2 ** i * digit_part[self.a - i - 2] for i in range(self.a - 1)]) - 2 ** (self.a - 1) * is_negative
        fraction = sum([(5 ** (i + 1)) * fraction_part[i] * (10 ** (self.b - i))for i in range(self.b)])
        
        if not is_negative:
            while fraction >= 1000:
                fraction //= 10
        else:
            digit += 1
            fraction = 10 ** len(str(fraction)) - fraction
            any_1 = False
            while fraction >= 1000:
                any_1 = any_1 or fraction % 10
                fraction //= 10
            fraction += int(any_1)
            
            if fraction == 1000:
                fraction = 0
                digit -= 1
        
        print(str(digit) + '.' + str(fraction).ljust(3, '0'))
                


def convert_to_binary(number16: str, reverse: bool = False) -> list:
    if not number16.startswith('0x'):
        print('Wrong input number (Should start with 0x)')
        exit(0)
    
    try:
        binary = bin(int(number16[2:], 16))[2:]
        binary = [int(i) for i in binary]
        if reverse:
            binary.reverse()
        
        return binary
    except ValueError:
        print("Wrong input number")
        exit(0)


def is_fixed_point(number_type):
    if number_type.count('.') == 1:
        a, b = number_type.split('.')
        if a.isdigit() and b.isdigit() and int(a) > 0 and int(a) + int(b) <= 32:
            return True
    
    return False


def check_number_type(number_type: str) -> bool:
    if not (number_type == 'h' or \
           number_type == 'f' or \
           is_fixed_point(number_type)):
        print("Invalid number type")
        exit(0)


def check_number_size(max_size: int, number1: list, number2: list = list()):
    if not (max_size >= len(number1) and max_size >= len(number2)):
        print("Number is too big")
        exit(0)


def check_round_method(round_method):
    if not round_method == ROUND_METHOD:
        print("Wrong round method. Can only process round toward negative infinity (3)")
        exit(0)


def round_and_print(number_type: str, number: str) -> None:
    if number_type == 'h':
        number = convert_to_binary(number)
        check_number_size(16, number)
        
        number = FloatingPointNumber(16, number)
        number.print()
    elif number_type == 'f':
        number = convert_to_binary(number)
        check_number_size(32, number)
        
        number = FloatingPointNumber(32, number)
        number.print()
    else:
        a, b = map(int, number_type.split('.'))
        
        number = convert_to_binary(number, reverse=True)
        check_number_size(a + b, number)
        
        number = FixedPointNumber(a, b, number)
        number.print()


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 3 and len(args) != 5:
        print("Wrong arguments count (need 3 or 5)")
        exit(0)

    number_type = args[0]
    check_number_type(number_type)
        
    round_method = args[1]
    check_round_method(round_method)
    
    if len(args) == 3:
        number = args[2]
        round_and_print(number_type, number)
    elif len(args) == 5:
        pass
