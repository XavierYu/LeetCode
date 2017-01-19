"""
 You are given a string, s, and a list of words, words, that are all of the same length. Find all starting indices of
 substring(s) in s that is a concatenation of each word in words exactly once and without any intervening characters.

For example, given:
s: "barfoothefoobarman"
words: ["foo", "bar"]

You should return the indices: [0,9].
(order does not matter).
"""

class Solution(object):
    def nextWord(self, s, words)

    def findSubstring(self, s, words):
        """
        :type s: str
        :type words: List[str]
        :rtype: List[int]
        """
        count = 0
        for word in words:
            count += len(word)

        if count == 0:
            return 0

        status = [[] for _ in range(0, len(words))]

        end  =  False

        while nextWord:





