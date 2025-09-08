import random

nombre = random.randint(0,100)
input1 = input("Devine mon chiffre : ")

if int(input1) == nombre :
    print("wow trop fort!")
else :
    print("non, mais tu peux réessayer")
    