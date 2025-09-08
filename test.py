import random

nombre = random.randint(0,100)
boucle = True

while boucle == True:

    
    input1 = input("Devine mon chiffre : ")

    try:
        if int(input1) == nombre :
            print("wow trop fort!")
            boucle = False
        else :
            print("non, mais tu peux réessayer")
    except:
        print("un CHIFFRE plz")
        
    