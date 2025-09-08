import random


chiffre1 = input("Donnez moi un premier chiffre : ")
chiffre2 = input("Donnez moi un deuxième chiffre : ")

nombre = random.randint(chiffre1,chiffre2)
boucle = True
essais = 0

while boucle == True:

    
    input1 = input(f"Devine mon chiffre situé entre {chiffre1} et {chiffre2} : ")
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
        
    