import time


class Solution(object):
    # 比较整体
    def strStr(self, haystack, needle):
        """
        :type haystack: str
        :type needle: str
        :rtype: int
        """
        max = len(haystack)
        target = len(needle)
        ret = -1
        if not needle:
            return 0
        if not max:
            return -1

        for i in range(0, max):
            if haystack[i] == needle[0]:
                if i + target - 1 < max:
                    if haystack[i:i + target] == needle:
                        ret = i
                        return ret
        return ret

    # 比较 str vs needle 的单独个体
    def strStr_improved(self, haystack, needle):
        """
        :type haystack: str
        :type needle: str
        :rtype: int
        """
        maximum = len(haystack)
        target = len(needle)
        if not target and not maximum:
            return 0
        ret = -1
        for i in range(0, maximum):
            count = 0
            for j in range(0, target):
                if i+j >= maximum:
                    return -1
                if haystack[i+j] != needle[j]:
                    break
                count += 1
            if count == target:
                return i
        return ret


input = ""
ans = Solution()
start = time.time()
result = ans.strStr(input, "")
end = time.time()
print "Time Used (ms): " + str((end - start)*1000)
print result
