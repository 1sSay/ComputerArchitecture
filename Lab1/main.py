import sys
from typing import Self

ROUND_METHOD = "3"


class FloatingPointNumber:
    def __init__(self, number: int, size: int) -> None:
        self.number = number
        self.size = size

        # default single precision
        self.mantissa_size = 24
        self.exp_size = 8
        self.bias = 127
        self.output_mantissa_size = 6

        self.inf = int('7f800000', 16)
        self.neg_inf = int('ff800000', 16)
        self.nan = int('7f800001', 16)

        self.zero = 0
        self.neg_zero = 1 << (size - 1)

        if size == 16:
            self.mantissa_size = 11
            self.exp_size = 5
            self.bias = 15
            self.output_mantissa_size = 3

            self.inf = int('7c00', 16)
            self.neg_inf = int('fc00', 16)
            self.nan = int('7c01', 16)

        self.mantissa = (number & ((1 << (self.mantissa_size - 1)) - 1))
        self.exp = ((number >> (self.mantissa_size - 1)) & ((1 << self.exp_size) - 1))

        self.sign = number >> (self.size - 1)

        self.is_nan = (self.exp == ((1 << self.exp_size) - 1)) and \
                      (self.mantissa != 0)
        self.is_positive_inf = (self.exp == ((1 << self.exp_size) - 1)) and \
                               (self.mantissa == 0) and not self.sign
        self.is_negative_inf = (self.exp == ((1 << self.exp_size) - 1)) and \
                               (self.mantissa == 0) and self.sign
        self.is_positive_zero = (self.exp == 0) and (self.mantissa == 0) and not self.sign
        self.is_negative_zero = (self.exp == 0) and (self.mantissa == 0) and self.sign
        self.is_subnormal = (self.exp == 0) and (self.mantissa != 0)

        if not self.is_subnormal:
            self.mantissa += (1 << (self.mantissa_size - 1))

    def shift(self, sign, exp, mantissa, mul=False):
        for_negative_round = 0
        while len(bin(mantissa)[2:]) > self.mantissa_size:
            for_negative_round = for_negative_round or (mantissa & 1)
            mantissa >>= 1
            if not mul:
                exp += 1

        if sign and for_negative_round:
            mantissa += 1
            if mantissa == (1 << self.mantissa_size):
                mantissa >>= 1

        while len(bin(mantissa)[2:]) < self.mantissa_size and exp > 0:
            mantissa <<= 1
            if not mul:
                exp -= 1

        return sign, exp, mantissa

    def __add__(self, second):
        if self.is_nan:
            return self
        if second.is_nan:
            return second

        if (self.is_positive_inf and second.is_negative_inf) or \
           (self.is_negative_inf and second.is_positive_inf):
            return FloatingPointNumber(self.nan, self.size)

        if self.is_positive_inf or second.is_positive_inf:
            return FloatingPointNumber(self.inf, self.size)
        if self.is_negative_inf or second.is_negative_inf:
            return FloatingPointNumber(self.neg_inf, self.size)

        if (self.is_positive_zero or self.is_negative_zero) and \
           (second.is_positive_zero or second.is_negative_zero):
            return FloatingPointNumber(self.neg_zero, self.size)

        if (self.is_positive_zero or self.is_negative_zero):
            return second
        if (second.is_positive_zero or second.is_negative_zero):
            return self

        exp_shift = min(self.exp, second.exp)

        shifted_mantissa1 = self.mantissa * (1 << (self.exp - exp_shift))
        shifted_mantissa2 = second.mantissa * (1 << (second.exp - exp_shift))

        if self.sign == second.sign:
            sign = self.sign
            mantissa = shifted_mantissa1 + shifted_mantissa2
        else:
            if shifted_mantissa1 >= shifted_mantissa2:
                mantissa = shifted_mantissa1 - shifted_mantissa2
                sign = self.sign
            else:
                mantissa = shifted_mantissa2 - shifted_mantissa1
                sign = second.sign

        sign, exp, mantissa = self.shift(sign, exp_shift, mantissa)


        if exp >= int('1' * self.exp_size, 2):
            if not sign:
                return FloatingPointNumber(self.inf, self.size)
            else:
                return FloatingPointNumber(self.neg_inf, self.size)

        if exp <= 0:
            while exp < 0 and mantissa > 0:
                mantissa >>= 1

            if mantissa == 0:
                return FloatingPointNumber(self.neg_zero, self.size)


        result = (sign << (self.size - 1))
        result += (exp << (self.mantissa_size - 1))
        result += mantissa & ((1 << (self.mantissa_size - 1)) - 1)

        return FloatingPointNumber(result, self.size)

    def __sub__(self, second):
        if self.is_nan:
            return self
        if second.is_nan:
            return second

        if (self.is_positive_inf and second.is_positive_inf) or \
           (self.is_negative_inf and second.is_negative_inf):
            return FloatingPointNumber(self.nan, self.size)

        if (self.is_positive_zero or self.is_negative_zero) and \
           (second.is_positive_zero or second.is_negative_zero):
            return FloatingPointNumber(self.neg_zero, self.size)

        if self.is_positive_inf:
            return FloatingPointNumber(self.inf, self.size)
        if self.is_negative_inf:
            return FloatingPointNumber(self.neg_inf, self.size)

        exp_shift = min(self.exp, second.exp)
        shifted_mantissa1 = self.mantissa * (1 << (self.exp - exp_shift))
        shifted_mantissa2 = second.mantissa * (1 << (second.exp - exp_shift))

        if self.sign != second.sign:
            sign = self.sign
            mantissa = shifted_mantissa1 + shifted_mantissa2
        else:
            if shifted_mantissa1 >= shifted_mantissa2:
                mantissa = shifted_mantissa1 - shifted_mantissa2
                sign = 0
            else:
                mantissa = shifted_mantissa2 - shifted_mantissa1
                sign = 1

        sign, exp, mantissa = self.shift(sign, exp_shift, mantissa)

        if exp >= int('1' * self.exp_size, 2):
            if not sign:
                return FloatingPointNumber(self.inf, self.size)
            else:
                return FloatingPointNumber(self.neg_inf, self.size)

        if exp <= 0:
            while exp < 0 and mantissa > 0:
                mantissa >>= 1

            if mantissa == 0:
                return FloatingPointNumber(self.neg_zero, self.size)

        result = (sign << (self.size - 1))
        result += (exp << (self.mantissa_size - 1))
        result += mantissa & ((1 << (self.mantissa_size - 1)) - 1)

        return FloatingPointNumber(result, self.size)

    def __mul__(self, second):
        if self.is_nan:
            return self
        if second.is_nan:
            return second
        
        if ((self.is_positive_zero or self.is_negative_zero) and (second.is_positive_inf or second.is_negative_inf)) or \
           ((second.is_positive_zero or second.is_negative_zero) and (self.is_positive_inf or self.is_negative_inf)):
            return FloatingPointNumber(self.nan, self.size)
        
        if (self.is_positive_inf and second.is_negetive_inf) or \
           (second.is_positive_inf and self.is_negative_inf):
            return FloatingPointNumber(self.nan, self.size)

        if self.is_negative_zero or self.is_positive_zero or \
           second.is_negative_zero or second.is_positive_zero:
           return FloatingPointNumber(self.neg_zero, self.size)

        sign = (self.sign + second.sign) & 1
        mantissa = self.mantissa * second.mantissa
        exp = self.exp + second.exp - self.bias

        if len(bin(mantissa)[2:]) == self.mantissa_size * 2:
            if sign:
                mantissa += 1
            mantissa >>= 1
            exp += 1

        sign, exp, mantissa = self.shift(sign, exp, mantissa, mul=True)

        if exp >= int('1' * self.exp_size, 2):
            if not sign:
                return FloatingPointNumber(self.inf, self.size)
            else:
                return FloatingPointNumber(self.neg_inf, self.size)

        if exp <= 0:
            while exp < 0 and mantissa > 0:
                mantissa >>= 1

            if mantissa == 0:
                return FloatingPointNumber(self.neg_zero, self.size)

        result = (sign << (self.size - 1))
        result += (exp << (self.mantissa_size - 1))
        result += mantissa & ((1 << (self.mantissa_size - 1)) - 1)

        return FloatingPointNumber(result, self.size)

    def __truediv__(self, second):
        if self.is_nan:
            return self
        if second.is_nan:
            return second

        if (self.is_negative_zero or self.is_positive_zero) and \
           (second.is_negative_zero or second.is_positive_zero):
           return FloatingPointNumber(self.nan, self.size)

        if (self.is_positive_inf or self.is_negative_inf) and \
           (second.is_positive_inf or second.is_negative_inf):
           return FloatingPointNumber(self.nan, self.size)

        if second.is_positive_zero:
            if not self.sign:
                return FloatingPointNumber(self.inf, self.size)
            else:
                return FloatingPointNumber(self.neg_inf, self.size)
        
        if second.is_negative_zero:
            if not self.sign:
                return FloatingPointNumber(self.neg_inf, self.size)
            else:
                return FloatingPointNumber(self.inf, self.size)


        sign = (self.sign + second.sign) & 1
        exp = self.exp - second.exp + self.bias
        mantissa = (self.mantissa << self.mantissa_size) // second.mantissa
        
        sign, exp, mantissa = self.shift(sign, exp, mantissa, mul=True)
        
        if exp >= int('1' * self.exp_size, 2):
            if not sign:
                return FloatingPointNumber(self.inf, self.size)
            else:
                return FloatingPointNumber(self.neg_inf, self.size)

        if exp <= 0:
            while exp < 0 and mantissa > 0:
                mantissa >>= 1

            if mantissa == 0:
                return FloatingPointNumber(self.neg_zero, self.size)

        result = (sign << (self.size - 1))
        result += (exp << (self.mantissa_size - 1))
        result += mantissa & ((1 << (self.mantissa_size - 1)) - 1)

        return FloatingPointNumber(result, self.size)

    def hex_mantissa(self, mantissa):
        result = ''

        length = len(bin(mantissa)[2:])
        mantissa <<= (4 - length % 4) + 1
        length += (4 - length % 4) + 1

        for i in range(length // 4):
            result += hex(mantissa & 15)[2:]
            mantissa >>= 4

        result = result[::-1]

        return result[:self.output_mantissa_size]

    def print(self) -> str:
        if self.is_nan:
            return "nan"
        if self.is_positive_inf:
            return "inf"
        if self.is_negative_inf:
            return "-inf"
        if self.is_positive_zero:
            return "0x0." + "0" * self.output_mantissa_size + "p+0"
        if self.is_negative_zero:
            return "-0x0." + "0" * self.output_mantissa_size + "p+0"
        if self.is_subnormal:
            prefix = '0x'
            if self.sign:
                prefix = '-0x'

            shifted_mantissa = self.mantissa
            shift_exp = 0
            while (shifted_mantissa >> self.mantissa_size - 1) == 0:
                shifted_mantissa <<= 1
                shift_exp += 1

            return prefix + '1.' + self.hex_mantissa(shifted_mantissa) + 'p' + str(self.exp - self.bias - shift_exp)

        prefix = '0x'
        if self.sign:
            prefix = '-0x'

        result = prefix + '1.'
        result += self.hex_mantissa(self.mantissa)
        result += 'p'
        if self.exp - self.bias >= 0:
            result += '+'
        result += str(self.exp - self.bias)

        return result

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
        inverted_second = ((1 << (self.a + self.b)) - 1) - second.number + 1
        result = (self.number + inverted_second) % (1 << (self.a + self.b))
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
            digit -= (1 << self.a)
            fraction = (1000 - fraction) % 1000

        if self.sign and fraction != 0:
            digit += 1

        result = ''
        if self.sign:
            result = '-'
        result += str(abs(digit)) + '.' + str(abs(fraction)).zfill(3)

        return result


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

    print(result.print())
