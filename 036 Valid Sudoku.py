

import time

class Solution(object):
    def isValidSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: bool
        """

        for i in range(0,9):
            nums = []
            for j in range(0,9):
                if board[i][j] != '.':
                    if board[i][j] not in nums:
                        nums.append(board[i][j])
                    else:
                        return False

        for i in range(0,9):
            nums = []
            for j in range(0,9):
                if board[j][i] != '.':
                    if board[j][i] not in nums:
                        nums.append(board[j][i])
                    else:
                        return False

        for i in range(0,9,3):
            for j in range(0,9,3):
                nums = []
                for m in range(i,i+3):
                    for k in range(j,j+3):
                        if board[m][k] != '.':
                            if board[m][k] not in nums:
                                nums.append(board[m][k])
                            else:
                                return False

        return True

nums = [".87654321","2........","3........","4........","5........","6........","7........","8........","9........"]
val = 0
ans = Solution()
start = time.time()*1000
result = ans.isValidSudoku(nums)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result