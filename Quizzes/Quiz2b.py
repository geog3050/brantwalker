mystr=input('Enter a list of numbers separated by commas:')
mylist = []

for i in mystr.split(','):
    mylist.append(int(i))

mylist.sort()

print(mylist[len(mylist)-2])
