mystr = str(input('Enter a string:'))
letter = str(input('What letter do you want to check for?'))

mylist = []

for i in mystr:
    mylist.append(i)

if mylist.count(letter)!=0:
    print('Yes')
else:
    print('No')
    
