"""
 Given a collection of candidate numbers (C) and a target number (T), find all unique combinations in C where the candidate numbers sums to T.

Each number in C may only be used once in the combination.

Note:

    All numbers (including target) will be positive integers.
    The solution set must not contain duplicate combinations.

For example, given candidate set [10, 1, 2, 7, 6, 1, 5] and target 8,
A solution set is:

[
  [1, 7],
  [1, 2, 5],
  [2, 6],
  [1, 1, 6]
]

"""

import time


class Solution(object):
    def combinationSum2(self, candidates, target):
        """
        :type candidates: List[int]
        :type target: int
        :rtype: List[List[int]]
        """
        res = []
        candidates.sort()
        #print candidates
        self.dfs(candidates, target, 0, [], res)
        return res

    def dfs(self, nums, target, index, path, res):
        if target < 0:
            return  # backtracking
        if target == 0:
            res.append(path)
            return
        for i in xrange(index, len(nums)):
            if i != index and nums[i] == nums[i-1]:
                continue
            self.dfs(nums, target - nums[i], i+1, path + [nums[i]], res)

nums = [10, 1, 2, 7, 6, 1, 5]
ans = Solution()
start = time.time()*1000
result = ans.combinationSum2(nums, 8)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result
