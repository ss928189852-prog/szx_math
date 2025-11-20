import math


# Calculate and return the LCM of a list of numbers
def LCM(num):
    minimum = 1
    for i in num:
        minimum = int(i)*int(minimum) / math.gcd(int(i), int(minimum))
    return int(minimum)
