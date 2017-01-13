"""
Given a linked list, swap every two adjacent nodes and return its head.

For example,
Given 1->2->3->4, you should return the list as 2->1->4->3.

Your algorithm should use only constant space.
You may not modify the values in the list, only nodes itself can be changed.

"""

from ListNodeHelpClass import*
import time


class Solution(object):
    def swapPairs(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        dummy = cur = pre = ListNode(0)
        count = 0
        while head:
            # print "debug"
            count += 1
            if count%2 == 0:
                pre.next = head
                pre = pre.next
                head = head.next
                pre.next = cur

            else:
                pre = cur
                cur.next = head
                cur = cur.next
                head = head.next
        cur.next = None
        return dummy.next


input = []
for i in range(0, 10000):
    input.append(i)
listNodeHelper = ListNodeHelpClass()
ans = Solution()
inputList1 = listNodeHelper.createListNodeFromListInput(input)
listNodeHelper.printLinkedListNode(inputList1)
start = (time.time()-1484122200)*1000
result = ans.swapPairs(inputList1)
print round((time.time()-1484122200)*1000)-start
re1 = listNodeHelper.printLinkedListNode(result)

