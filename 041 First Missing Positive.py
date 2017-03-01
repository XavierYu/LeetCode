"""
 Given an unsorted integer array, find the first missing positive integer.

For example,
Given [1,2,0] return 3,
and [3,4,-1,1] return 2.
"""

import time


class Solution(object):
    def firstMissingPositive(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        if not nums or nums ==[]:
            return 1
        nums.sort()
        cur = 0
        for i in xrange(0, len(nums)):
            if nums[i] < 0:
                continue
            if nums[i] - cur == 1:
                cur += 1
            elif nums[i] - cur > 1:
                return cur+1
        return cur +1



nums = [0,2,2,1,1]
ans = Solution()
start = time.time()*1000
result = ans.firstMissingPositive(nums)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result
