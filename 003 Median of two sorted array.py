# Median of two sorted array


# method: 取中间Index，一个一个提取，直到count reach index
class Solution(object):
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        
        lenA = len(nums1)
        lenB = len(nums2)
        totalLength =  lenA + lenB
        medianIndex = None
        if totalLength%2 == 0:
            medianIndex = totalLength/2 +0.5
        else:
            medianIndex = int(totalLength/2) + 1.0
        m = 0
        n = 0
        count = 0
        median = 0
        while (True):            
            if m == lenA:
                medianCurr = nums2[n]
                n= n+1
            elif n == lenB:
                medianCurr = nums1[m]
                m =m+1
            elif nums1[m]<=nums2[n]:
                medianCurr = nums1[m]
                m=m+1
            else:
                medianCurr = nums2[n]
                n=n+1
            count= count+1
            
            if medianIndex -count <1:
                if medianIndex == count:
                    median = medianCurr
                    break
                elif medianIndex - count == 0.5:
                    median += medianCurr*0.5
                elif medianIndex - count == -0.5:
                    median += medianCurr*0.5
                    break
        return median