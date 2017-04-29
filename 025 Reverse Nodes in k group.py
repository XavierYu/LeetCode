"""
 Given a linked list, reverse the nodes of a linked list k at a time and return its modified list.

k is a positive integer and is less than or equal to the length of the linked list.
If the number of nodes is not a multiple of k then left-out nodes in the end should remain as it is.

You may not alter the values in the nodes, only nodes itself may be changed.

Only constant memory is allowed.

For example,
Given this linked list: 1->2->3->4->5

For k = 2, you should return: 2->1->4->3->5

For k = 3, you should return: 3->2->1->4->5
"""

from ListNodeHelpClass import*
import time


class Solution(object):
    def reverseKGroup1(self, head, k):
        """
        :type head: ListNode
        :type k: int
        :rtype: ListNode
        """
        dummy = cur = ListNode(0)
        count = 0
        stack = []
        while head:
            count = count +1
            stack.append(head)
            head = head.next
            if count%k == 0:
                while stack:
                    cur.next = stack.pop()
                    cur = cur.next
        for item in stack:
            cur.next = item
            cur = cur.next
        cur.next = None
        return dummy.next

    def reverseKGroup(self, head, k):
        """
        :type head: ListNode
        :type k: int
        :rtype: ListNode
        """
        cur = head
        count = 0
        while cur and count != k:
            count += 1
            cur = cur.next

        if count == k:
            cur = self.reverseKGroup(cur,k)

            while count > 0:
                temp = head.next
                head.next = cur
                cur = head
                head =temp
                count -= 1
            head = cur
        return head



input = []
for i in range(0, 200):
    input.append(i)
listNodeHelper = ListNodeHelpClass()
ans = Solution()
inputList1 = listNodeHelper.createListNodeFromListInput(input)
listNodeHelper.printLinkedListNode(inputList1)

start = (time.time()-1484304140)*1000
result = ans.reverseKGroup(inputList1, 2)
print round((time.time()-1484304140)*1000)-start
re1 = listNodeHelper.printLinkedListNode(result)


