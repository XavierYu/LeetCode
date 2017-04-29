"""
Problem Decription:

Implement regular expression matching with support for '.' and '*'.

'.' Matches any single character.
'*' Matches zero or more of the preceding element.

The matching should cover the entire input string (not partial).

The function prototype should be:
bool isMatch(const char *s, const char *p)

"""

"""
Resources:

Dynamic Programming in Java:
https://www.topcoder.com/community/data-science/data-science-tutorials/dynamic-programming-from-novice-to-advanced/


"""

"""
Tips: initialize [][] list in python
http://ars.me/programming/2014/06/14/py-listmul/
l = [[] for _ in range(3)]

l = [[]]*3 wrong  [] is a pointer referenced to list, mutable, all 3 pointing to same object
l = [0]*3 correct immutable object
"""
class Solution(object):
    def isMatch(self, s, p):
        """
        :type s: str
        :type p: str
        :rtype: bool
        """
        if s==None or p == None:
            return False
        sp = [[False]*(len(p)+1) for i in range(0, len(s)+1)]
        sp[0][0]=True
        for i in range(1, len(p)+1):
            if p[i-1]=='*':
                sp[0][i] = sp[0][i-1] or sp[0][i-2]
        
        for i in range(1, len(s)+1):
            s_index = i-1
            for j in range(1, len(p)+1):
                p_index = j-1
                if p[p_index] == '.':
                    sp[i][j] = sp[i-1][j-1]
                if s[s_index]==p[p_index]:
                    sp[i][j] = sp[i-1][j-1]
                if p[p_index] == '*':
                    if p[p_index-1] != s[s_index] and p[p_index-1]!= '.':
                        sp[i][j] = sp[i][j-2]
                    else:
                        sp[i][j] = sp[i][j-1] or sp[i][j-2]or sp[i-1][j]
        #print sp
        return sp[len(s)][len(p)]
        
ans = Solution()
s= ""
p= "*"
result  = ans.isMatch(s,p)
print result


