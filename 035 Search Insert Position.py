# coding=utf-8
"""
Given a sorted array and a target value, return the index if the target is found. If not, return the index where it
would be if it were inserted in order.

You may assume no duplicates in the array.

Here are few examples.
[1,3,5,6], 5 → 2
[1,3,5,6], 2 → 1
[1,3,5,6], 7 → 4
[1,3,5,6], 0 → 0

"""

import time


class Solution(object):
    def searchInsert(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        if not nums:
            return 0
        end = len(nums) -1
        start = 0
        if target < nums[0]:
            return 0
        elif target > nums[end]:
            return end+1

        while 1:
            mid = (start + end)/2
            if target > nums[mid]:
                start = mid
            elif target < nums[mid]:
                end = mid
            else:
                return mid
            if end-start == 1:
                return end

    def searchInsert_beat98(self, nums, key):
        if key > nums[len(nums) - 1]:
            return len(nums)

        if key < nums[0]:
            return 0

        l, r = 0, len(nums) - 1
        while l <= r:
            m = (l + r) / 2
            if nums[m] > key:
                r = m - 1
                if r >= 0:
                    if nums[r] < key:
                        return r + 1
                else:
                    return 0

            elif nums[m] < key:
                l = m + 1
                if l < len(nums):
                    if nums[l] > key:
                        return l
                else:
                    return len(nums)
            else:
                return m

nums = [1,3,5]
val = 2
ans = Solution()
start = time.time()*1000
result = ans.searchInsert(nums, val)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result