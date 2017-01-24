import time


class Solution(object):
    def nextPermutation(self, nums):
        """
        :type nums: List[int]
        :rtype: void Do not return anything, modify nums in-place instead.
        """

        # Find non-increasing suffix
        i = len(nums) - 1
        while i > 0 and nums[i - 1] >= nums[i]:
            i -= 1
        if i <= 0:
            nums.sort()
        else:
            # Find successor to pivot
            j = len(nums) - 1
            while nums[j] <= nums[i - 1]:
                j -= 1
            nums[i - 1], nums[j] = nums[j], nums[i - 1]

            # Reverse suffix
            nums[i:] = nums[len(nums) - 1: i - 1: -1]
        # return nums

input = [5, 6, 7, 9, 4, 3, 5, 9, 6]

ans = Solution()
start = time.time()*1000
ans.nextPermutation(input)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print input