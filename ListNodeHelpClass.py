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
        if input ==[]:
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
        print "listnode: " + str(ret)
        return ret

    def createListOfListNodeFromListOfList(self, input):
        ret= []
        for i in range(0,len(input)):
            newListNode = self.createListNodeFromListInput(input[i])
            ret.append(newListNode)
        return ret

    def printListOfLinkedListNode(self,input):
        ret = [[] for _ in range(0,len(input))]
        for i in range(0,len(input)):
            cur = input[i]
            while (cur is not None):
                ret[i].append(cur.val)
                cur = cur.next
        print "List of listnode: " + str(ret)
        return ret


