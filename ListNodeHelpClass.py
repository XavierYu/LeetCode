# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None


class ListNodeHelpClass(object):

    def createListNodeFromListInput(self, var):
        """
        rtype = ListNode
        input = List
        """
        if not var:
            return None
        l1 = cur = ListNode(var[0])
        for i in range(1, len(var)):
            newListNode = ListNode(var[i])
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
        while cur is not None:
            ret.append(cur.val)
            cur = cur.next
        print "listnode: " + str(ret)
        return ret

    def createListOfListNodeFromListOfList(self, var):
        ret= []
        for i in range(0, len(var)):
            newListNode = self.createListNodeFromListInput(var[i])
            ret.append(newListNode)
        return ret

    def printListOfLinkedListNode(self, var):
        ret = [[] for _ in range(0, len(var))]
        for i in range(0, len(var)):
            cur = var[i]
            while cur is not None:
                ret[i].append(cur.val)
                cur = cur.next
        print "List of listnode: " + str(ret)
        return ret
