class Solution(object):
    #BY INT to STRING Conversion
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """
        if x < 0:
            return False
        strCopy = str(x)
        length = len(strCopy)
        isPalindrone  = True
        for i in range(0, length/2):
            if strCopy[i] == strCopy[length-1-i]:
                continue
            else:
                isPalindrone  = False
                break
        return isPalindrone
        
    #Digit monipulation
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """     
        if x < 0:
            return False
        reVal = 0
        y = x
        while(x>0):
            reVal = reVal*10+x%10
            x = x/10
        return y == reVal
        
    #Improved: compare half of the digits
     def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        """     
        if x < 0:
            return False
        reVal = 0
        while(x>reVal):#-----------Slower due to this comparison
            reVal = reVal*10+x%10
            x = x/10
        return (x == reVal or x == reVal/10)              