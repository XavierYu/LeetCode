"""
Given an array of integers sorted in ascending order, find the starting and ending position of a given target value.

Your algorithm's runtime complexity must be in the order of O(log n).

If the target is not found in the array, return [-1, -1].

For example,
Given [5, 7, 7, 8, 8, 10] and target value 8,
return [3, 4].
"""

"""
解题思路：
1） 前后趋紧
2） binarysearch 第一个target, 接着binarysearch for next value bigger than target
"""

import time

class Solution(object):
    def searchRange(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        ret = [-1, -1]
        start = 0
        end = len(nums)-1

        while start <= end:
            if nums[start] == nums[end] == target:
                return [start, end]
            if nums[start] > target or nums[end] < target:
                break
            if nums[start] < target:
                start += 1
            if nums[end] > target:
                end -= 1
        return [-1 , -1]


nums = [-1]
val = 0
ans = Solution()
start = time.time()*1000
result = ans.searchRange(nums, val)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result