import time
import random

intA = random.randint(0, 100)
# intB = random.randint(0,15.0*10)/10.0
intB = random.random()*15.0
print (intA, str(intB))
lists =[None,None,[1,2,3]]
del lists[-1]
print lists

# ret = 1
# for i in range(1,19):
#     ret = ret * i
#
# print ret