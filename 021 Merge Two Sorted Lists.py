# Definition for singly-linked list.
class ListNode(object):
     def __init__(self, x):
         self.val = x
         self.next = None

class ListNodeHelpClass(object):
    def createListNodeFromListInput(self, input):
        """
        rtype = ListNode
        input = List
        """
        if input ==None:
            return None
        l1 = cur = ListNode(input[0])
        for i in range(1, len(input)):
            newListNode = ListNode(input[i])
            cur.next = newListNode
            cur = cur.next
        return l1

    def printLinkedListNode(self, l1):
        """
        :type l1: ListNode
        :rtype: List
        """
        cur = l1
        ret = []
        while(cur != None):
            ret.append(cur.val)
            cur = cur.next
        print ret


class Solution(object):
    def mergeTwoLists(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        if l1 ==None:
            return l2
        if l2 == None:
            return l1
        curL1 = l1
        curL2 = l2
        dummy=end = ListNode(0)
        while(curL1 != None or curL2 != None):
            if curL1 ==None:
                end.next = curL2
                break
            if curL2 ==None:
                end.next = curL1
                break
            nextL1 = curL1.next
            nextL2 = curL2.next
            if curL1.val < curL2.val:
                end.next = curL1
                curL1 = nextL1
            else:
                end.next = curL2
                curL2 = nextL2
            end = end.next
        return dummy.next
    
    
input1 = [0,1,2,3,4,5,6]
input2 = [0,1,2,3]
listNodeHelper = ListNodeHelpClass()
l1 = listNodeHelper.createListNodeFromListInput(input1)
l2 = listNodeHelper.createListNodeFromListInput(input2)

ans = Solution()
result = ans.mergeTwoLists(l1,l2)
listNodeHelper.printLinkedListNode(result)



    
                
