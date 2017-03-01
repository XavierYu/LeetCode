"""
Given n non-negative integers representing an elevation map where the width of each bar is 1,
compute how much water it is able to trap after raining.

For example,
Given [0,1,0,2,1,0,1,3,2,1,2,1], return 6.
"""
import time


class Solution(object):
    def trap(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        if len(height)< 3:
            return 0

        l = 0
        r = len(height)-1
        #print (l, r)
        ans = 0
        left = right = 0
        while(l < r):
            left = max(left, height[l])
            right = max(right, height[r])
            if left < right:
                ans += left - height[l]
                l += 1
                #print ('left', ans)
            else:
                ans += right - height[r]
                r -= 1
                #print ('right', ans)
        return ans

nums = [4,2,0,3,2,5,9,100,90,1000]
ans = Solution()
start = time.time()*1000
result = ans.trap(nums)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result


