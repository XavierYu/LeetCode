# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution(object):
    def removeNthFromEnd(self, head, n):
        """
        :type head: ListNode
        :type n: int
        :rtype: ListNode
        """
        Nodes = [head]
        count = 1
        while(Nodes[-1].next !=None):
            Nodes.append(Nodes[-1].next)
            count +=1
        if n ==count:
            return Nodes[0].next
        if n == 0:
            return Nodes[0]
        if n == 1:
            Nodes[-1-1].next =None
            return Nodes[0]
        Nodes[-n-1].next =Nodes[-n+1]
        return Nodes[0]
