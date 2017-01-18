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
    def reverseKGroup(self, head, k):
        """
        :type head: ListNode
        :type k: int
        :rtype: ListNode
        """
        dummy = cur = ListNode(0)
        count = 0
        stack = []
        while head:
            count += 1
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

    def reverseKGroup_improved(self, head, k):
        """
        :type head: ListNode
        :type k: int
        :rtype: ListNode
        """
        cur = head
        count = 0
        while cur and count != k:
            cur = cur.next
            count += 1

        if count == k:
            cur = self.reverseKGroup_improved(cur,k)
            while count > 0:
                temp = head.next
                head.next = cur
                cur = head
                head = temp
                count -= 1
            head = cur

        return head

    def reverseKGroup_NoneRecursion(self, head, k):
        """
        :type head: ListNode
        :type k: int
        :rtype: ListNode
        """

        if head is None or head.next is None or k == 1:
            return head

        dummy = ListNode(-1)
        dummy.next = head
        begin = dummy
        i = 0
        while head:
            i += 1

            if i%k == 0:
                begin = self.reverse(begin, head.next)
                head = begin.next
            else:
                head = head.next

        return dummy.next

    def reverse(self, begin, end):

        head = ret = begin.next
        cur = end
        while head != end:
            #print "debug"
            begin.next = head
            temp = head.next
            head.next = cur
            cur = head
            head = temp
        return ret








input = []
for i in range(1, 1):
    input.append(i)
listNodeHelper = ListNodeHelpClass()
ans = Solution()
inputList1 = listNodeHelper.createListNodeFromListInput(input)
listNodeHelper.printLinkedListNode(inputList1)

start = time.time()
result = ans.reverseKGroup_NoneRecursion(inputList1, 3)
# result = ans.reverse(inputList1, inputList1.next.next.next)
end = time.time()
print (end-start)*1000
re1 = listNodeHelper.printLinkedListNode(result)
# re1 = listNodeHelper.printLinkedListNode(inputList1)