"""
Write a program to solve a Sudoku puzzle by filling the empty cells.

Empty cells are indicated by the character '.'.

You may assume that there will be only one unique solution.
"""

"""
Tips:

"""

import time


class Solution(object):
    def solveSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        if not board or len(board) == 0:
            pass
        else:
            self.solve(board)

    def isValidSudoku(self, board, row, col, c):
        for idx in range(0, len(board)):
            if board[row][idx] != '.' and board[row][idx] == c:
                return False
            if board[idx][col] != '.' and board[idx][col] == c:
                return False
            if board[3*(row/3) + idx/3][3*(col/3) + idx%3] != '.' and board[3*(row/3) + idx/3][3*(col/3) + idx%3] == c:
                return False
        return True

    def solve(self, board):
        for i in range(0, 9):
            for j in range(0, 9):
                if board[i][j] == '.':
                    for num in range(1, 10):
                        if self.isValidSudoku(board, i, j, str(num)):
                            board[i][j] = str(num)
                            #tempboard = list(board)
                            if self.solve(board):
                                #board = tempboard
                                return True
                            else:
                                board[i][j] = '.'
                    return False
        return True

nums = ["..9748...","7........",".2.1.9...","..7...24.",".64.1.59.",".98...3..","...8.3.2.","........6","...2759.."]
board = []
for i in range(0,9):
    newlist = []
    board.append(newlist)
    for j in range(0,9):
        board[i].append(nums[i][j])

ans = Solution()
start = time.time()*1000
result = ans.solveSudoku(board)
end = time.time()*1000
print "Time Used (ms): " + str((end - start))
print result









