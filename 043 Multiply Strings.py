"""
Given two non-negative integers num1 and num2 represented as strings, return the product of num1 and num2.

Note:

    The length of both num1 and num2 is < 110.
    Both num1 and num2 contains only digits 0-9.
    Both num1 and num2 does not contain any leading zero.
    You must not use any built-in BigInteger library or convert the inputs to integer directly.

"""


import time


class Solution(object):
    def multiply(self, num1, num2):
        """
        :type num1: str
        :type num2: str
        :rtype: str
        """
        value1 = value2 = 0

        for char in num1:
            value1 = value1*10 + ord(char) - 48

        for char in num2:
            value2 = value2*10 + ord(char) - 48

        return self.toString(value1*value2)

    def toString(self, num):
        ret = ''
        if num == 0:
            return '0'
        while num/10:
            remainder = str(num%10)
            num /= 10
            ret = remainder + ret
        if num != 0:
            ret = str(num) + ret
        return ret

A = "0"
B = "0"
ans = Solution()
start = time.time()*1000
result = ans.multiply(A, B)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result