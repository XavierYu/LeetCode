class Solution(object):
    def fourSum(self, nums, target):
        """
            :type nums: List[int]
            :type target: int
            :rtype: List[List[int]]
            """
        
        nums.sort()
        print nums
        ret = []
        for i in range(0, len(nums)-3):
            if(i>0 and nums[i]==nums[i-1]):
                continue
            if(nums[i]+nums[i+1]+nums[i+2]+nums[i+3]>target):
                break
            if(nums[i]+nums[n-3]+nums[n-2]+nums[n-1]<target):
                continue
            for j in range(index2nd, len(nums)-2):
                if j==index2nd or (j>index2nd and nums[j] != nums[j-1]):
                    lo = j+1
                    hi = len(nums)-1
                    diff = target - nums[i]-nums[j]
                    print (i,j,lo,hi)
                    while(lo < hi):
                        print (lo,hi)
                        if nums[hi]+nums[lo] == diff:
                            print ('found',i,j,lo,hi)
                            ret.append([nums[i],nums[j],nums[lo],nums[hi]])
                            lo += 1
                            hi -= 1
                            while nums[lo] == nums[lo-1] and lo<len(nums)-1:
                                lo +=1
                            while nums[hi] == nums[hi+1] and hi>=0:
                                hi -=1
                        elif nums[hi]+nums[lo]< diff:
                            lo += 1
                        elif nums[hi]+nums[lo]> diff:
                            hi -= 1
        return ret

ans = Solution()
nums= [0,0,0,0]
target= 0
result  = ans.fourSum(nums,target)
print result
