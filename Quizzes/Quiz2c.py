mystr = input('Enter a list of numbers separated by commas:')
mylist=[]

for i in mystr.split(','):
    mylist.append(int(i))

count=0

for i in mylist:
    if mylist.count(i)>1:
        count+=1

if count==0:
    print('This list provided does not contain duplicate values')
else:
    print('This list provided contains duplicate values')
