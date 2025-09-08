import random



nombre = random.randint(0,100)
boucle = True
essais = 0

while boucle == True:

    
    input1 = input("Devine mon chiffre : ")
    essais +=1 

    try:
        if int(input1) == nombre :
            # Si le chiffre est le bon
            print("wow trop fort!")
            boucle = False
            
        else :
            # Si le chiffre n'est pas le bon
            print("non, mais tu peux réessayer")
            
    except:
        # permet de ne pas faire arrêter le programme
        print("un CHIFFRE plz")
        
print("nombre d'essais :", essais)
print("Bye !")
        
    