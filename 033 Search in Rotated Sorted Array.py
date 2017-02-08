"""
Suppose an array sorted in ascending order is rotated at some pivot unknown to you beforehand.

(i.e., 0 1 2 4 5 6 7 might become 4 5 6 7 0 1 2).

You are given a target value to search. If found in the array return its index, otherwise return -1.

You may assume no duplicate exists in the array.

Subscribe to see which companies asked this question.

"""
"""
解题思路：
1） 比较第一个， 小的化反向搜索， 大的话正向搜索
"""


import time

class Solution(object):
    def search(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        if not nums:
            return -1

        number = len(nums)
        if target == nums[0]:
            return 0
        elif target > nums[0]:
            for idx in range(0, number):
                if nums[idx] < nums[0]:
                    return -1
                if target == nums[idx]:
                    return idx
                elif target < nums[idx]:
                    return -1
            return -1
        elif target < nums[0]:
            for idx in range(-1, number*(-1)-1, -1):
                if nums[idx] > nums[0]:
                    return -1

                if target == nums[idx]:
                    return number+ idx
                elif target > nums[idx]:
                    return -1
            return -1


    # while loop is faster than for loop(not confirmed)
    def search_faster(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        if not nums:
            return -1
        if target == nums[0]:
            return 0
        elif target > nums[0]:
            idx = 0
            while True:
                if idx >= len(nums):
                    return -1
                if nums[idx] < nums[0]:
                    return -1
                if target > nums[idx]:
                    idx += 1
                elif target == nums[idx]:
                    return idx
                elif target < nums[idx]:
                    return -1
        elif target < nums[0]:
            idx = -1
            while True:
                if idx < len(nums) * (-1):
                    return -1
                if nums[idx] > nums[0]:
                    return -1
                if target < nums[idx]:
                    idx -= 1
                elif target == nums[idx]:
                    return len(nums)+ idx
                elif target > nums[idx]:
                    return -1


nums = [3,1]
val = 1
ans = Solution()
start = time.time()*1000
result = ans.search(nums, val)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result
