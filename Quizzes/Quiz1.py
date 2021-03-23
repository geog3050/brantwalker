x = str(input('What Climate are we in? (no spaces or misspellings please) '))
y = eval(input('What are the temperature measurements? '))

def Folding(x,y):
    for i in y:
        if type(i)!=int and type(i)!=float:
            print('You did not give me a numerical measurement.')
            return
        if x == 'Tropical':
            if i <=30:
                print('F')
            else:
                print('U')
        elif x == 'Continental':
            if i <=25:
                print('F')
            else:
                print('U')
        else:
            if i<=18:
                print('F')
            else:
                print('U')

Folding(x,y)

# Professor solution, mine had inefficient code?
def folding(climate, tempList):
    threshold=18
    if climate=="Tropical":
        threshold=30
    elif climate=="Continental":
        threshold=25

    for temp in tempList:
        if temp<= threshold:
            print("P")
        else: print("U")

folding("Arctic", [15,23,45,32])

#Writing for possible errors
def myfunction(climate, tempList):      
    try:
        if not isinstance(climate,str):
            print("The first variable {} should be a string")
            raise ValueError
        if not isinstance(tempList, list):
            raise ValueError
            
        threshold=18
        if climate=="Tropical":
            threshold=30
        elif climate=="Continental":
            threshold=25

        for temp in tempList:
            if temp<= threshold:
                print("P")
            else: print("U")

    except ValueError:
        print('Input values are incorrect')


myfunction(12, [15,23,45,32])
