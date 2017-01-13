
lists =[None,None,[1,2,3]]

for item in lists:
    print item
    if item is not None:
        empty = False
        print ('Debug Break')
        break
    else:
        lists.remove(item)
print lists