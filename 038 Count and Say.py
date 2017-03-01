"""
The count-and-say sequence is the sequence of integers beginning as follows:
1, 11, 21, 1211, 111221, ...

1 is read off as "one 1" or 11.
11 is read off as "two 1s" or 21.
21 is read off as "one 2, then one 1" or 1211.

Given an integer n, generate the nth sequence.

Note: The sequence of integers will be represented as a string.

Subscribe to see which companies asked this question.
"""




import time

class Solution(object):
    def countAndSay(self, n):
        """
        :type n: int
        :rtype: str
        """
        var = "1"
        if n == 1:
            return var
        for _ in range(0, n-1):
            var = self.nextStr(var)
        return var

    def nextStr(self, var):
        cur = ''
        count = 0
        ret = ''
        for char in var:
            next = char
            if next != cur:
                if count != 0:
                    ret = ret + str(count)+ cur
                count = 1
            else:
                count += 1
            cur = next
        if count != 0:
            ret = ret + str(count) + cur
        return ret

nums = 5
ans = Solution()
start = time.time()*1000
result = ans.countAndSay(nums)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result