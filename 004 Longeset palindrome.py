# Median of two sorted array

#method 1: loop(longest possile to 1, 比如把 len= 3的 substring 一个一个check)
#Brute force, Rejected， too slow
class SolutionA(object):
    def Search(self, start, length, s):
        status = True
        #print (s[start:start+length])
        for i in range(0,length):
            if s[start+i]!=s[start+length-1-i]:
                status = False
            if status == False:
                break
        return status
                
    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        retString = None
        lengthMax = len(s)
        #print (lengthMax)
        while (True):
            for length in range(lengthMax,0,-1):
                #print (length)
                for startIndex in range(0,lengthMax-length+1):
                    #print (startIndex)
                    flagFind = self.Search(startIndex,length,s)
                    #print (flagFind)
                    if flagFind == True:
                        retString = s[startIndex:startIndex+length]
                        print (startIndex)
                        break
                if flagFind ==  True:
                    break
            if flagFind ==  True:
                break           
        return retString

ApproachA  = SolutionA()
testStrA = "abcdedcbafgvrnyitusobwcxgwlwniqchfnssqttdrnqqcsrigjsxkzcmuoiyxzerakhmexuyeuhjfobrmkoqdljrlojjjysfdslyvckxhuleagmxnzvikfitmkfhevfesnwltekstsueefbrddxrmxokpaxsenwlgytdaexgfwtneurhxvjvpsliepgvspdchmhggybwupiqaqlhjjrildjuewkdxbcpsbjtsevkppvgilrlspejqvzpfeorjmrbdppovvpzxcytscycgwsbnmspihzldjdgilnrlmhaswqaqbecmaocesnpqaotamwofyyfsbmxidowusogmylhlhxftnrmhtnnljjhhcfvywsqimqxqobfsageysonuoagmmviozeouutsiecitrmkypwknorjjiaasxfhsftypspwhvqovmwkjuehujofiabznpipidhfxpoustquzyfurkcgmioxacleqdxgrxbldcuxzgbcazgfismcgmgtjuwchymkzoiqhzaqrtiykdkydgvuaqkllbsactntexcybbjaxlfhyvbxieelstduqzfkoceqzgncvexklahxjnvtyqcjtbfanzgpdmucjlqpiolklmjxnscjcyiybdkgitxnuvtmoypcdldrvalxcxalpwumfx"
testStrB = "abc"
print (ApproachA.longestPalindrome(testStrA))
