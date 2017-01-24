import time


class Solution(object):
    def longestValidParentheses(self, s):
        """
        :type s: str
        :rtype: int
        """
        # create  a window that num of ( >= num of )
        # num of ) within the window is the cur longest valid parentheses
        # travel throungh s, re-position start of window to next (

        while s[-1] == "(":
            s = s[:-1]

        start = 0
        end = 0
        total = len(s)
        ret = 0
        opened = 0
        closed = 0
        cur = 0

        while total - start > ret and total - start > 1:
            while end < total and closed <= opened:
                if s[end] == '(':
                    opened += 1
                else:
                    closed += 1
                end += 1

                if closed == opened:
                    cur = closed *2
                if cur > ret:
                    ret = cur
                    print ("debug 111", ret)
            print ("debug 1",start, end, opened, closed, ret)
            # time.sleep(2)

            if end == total:
                while s[-1] == "(":
                    s.remove(s[-1])
                    total -= 1
                    opened -= 1
                    end = total
                while start < end and (opened > closed or s[start] == ")"):
                    if s[start] == '(':
                        opened -= 1
                    else:
                        closed -= 1

                    if opened == closed and start!= total and s[start] == "(":
                        cur = closed * 2
                        if cur > ret:
                            ret = cur
                            print ("debug 222", ret)
                    start += 1
                    print ("debug 2", start, end, opened, closed, ret)
            else:
                start = end
                end = start
                opened = 0
                closed = 0

        return ret

inputStr = "))))((()((()()(("
ans = Solution()
start = time.time()*1000
result = ans.longestValidParentheses(inputStr)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result
