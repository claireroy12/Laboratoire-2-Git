# -----------------------------------------------------------------------------
# Script : projet1.py
# Auteur : Claire-Isabelle Roy
# Description : surveille différents paramètres de fonctionnement des machines via SSH
# Paramètres : -x-
# Date : 2025-03-20
# -----------------------------------------------------------------------------
import paramiko
from datetime import datetime
import pandas as pd

def cvsToDataF(nomFichier):
    
    df = pd.read_csv(nomFichier, sep=',')
    df.columns = df.columns.str.strip()
    return df

def connexionSSH(df, index):
    
    #initialisation du client à surveiller
    addIP = df.loc[index, "Adresse IP"]
    port = 22
    user = df.loc[index, "user"]
    mdp = df.loc[index, "mdp"]
    
    #connexion au client
    client = paramiko.SSHClient()
    
    # Charger la politique de clés manquantes
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("*************************************Connexion SSH vers la machine", addIP, "...")
    message = "*************************************Connexion SSH vers la machine" + addIP + "..."
    
    #-------------------appel pour les logs
    gestionLogs(message) 
    
    try:
        client.connect(hostname=addIP, port=port, username=user, password = mdp) #connexion au client...
        return client
        
    except Exception :
        print("\033[31mImpossible d'établir une connexion SSH vers la machine", addIP, "\033[0m \n")
        message = "Impossible d'établir une connexion SSH vers la machine " + addIP
        #-------------------appel pour les logs
        gestionLogs(message)
        return None
      
def versionOS(client, système):
    try:
        
        #variables 
        os_name=""
        os_version=""
        version=""
        
        if système == "Windows": #pour windows
            stdin, stdout, stderr = client.exec_command("systeminfo") #fait la commande dans la connexion SSH (retourne une tuple)
            os_info = stdout.read().decode() #lie la réponse 
            
            for line in os_info.splitlines():
                if "OS Name" in line: #prend dans les informations du résulat de la commande juste la partie qui affiche la version de l'OS
                    os_name = line.split(":")[1].strip() #le champs après les :
                    
                if "OS Version" in line:
                    os_version = line.split(":")[1].split()[0].strip() #seulement le champ après les : (sépare avec : et sépare avec " ") puis enlève le caractères innutiles
                    break
                
            version = os_name + " " + os_version  #met le nom et la version ensemble    
                         
        elif système == "Linux": #pour linux
            stdin, stdout, stderr = client.exec_command("lsb_release -d") #fait la commande dans les guillemets dans la connexion SSH (et la met dans stdout)
            os_info = stdout.read().decode()
            
            for line in os_info.splitlines():
                if "Description" in line: 
                    version = line.split(":")[1].strip()
                    
        print("Version OS:", version)
        message = "Version OS:  " +  version
        #-------------------appel pour les logs
        gestionLogs(message)
            
    except Exception as e:
        print("il y a eu un problème pendant la commande pour version du client :", e)
    
def chargeCPU(client, système):
    
    try:
        if système == "Windows": #pour windows
                stdin, stdout, stderr = client.exec_command(r"powershell -Command (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue") #fait la commande dans la connexion SSH (retourne une tuple)
                CPUcharge = stdout.read().decode() 
                roundedCPUcharge = round(float(CPUcharge), 2)    #lie la réponse (limite à deux chiffres après la virgule)       
        elif système == "Linux": #pour linux
                stdin, stdout, stderr = client.exec_command(r"top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'") #additionne la colonne CPU (ligne utilisateur et système) dans la commande top
                CPUcharge = stdout.read().decode()
                roundedCPUcharge = round(float(CPUcharge), 2)  #lie la réponse (limite à deux chiffres après la virgule)
                
        print("Charge CPU:", roundedCPUcharge, "%" )
        message = "Charge CPU:  " + str(roundedCPUcharge) + "%" 
        #-------------------appel pour les logs
        gestionLogs(message)
        
            
    except Exception as e:
        print("il y a eu un problème pendant la commande pour charge CPU du client :", e)

def ramDisponible(client, système):
    
    try:
        if système == "Windows": #pour windows
            
                #cheche la RAM libre
                stdin, stdout, stderr = client.exec_command(r"powershell -Command (Get-Counter '\Memory\Available Bytes').CounterSamples.CookedValue / 1GB") #fait la commande dans la connexion SSH (retourne une tuple)
                ramLibre = stdout.read().decode() #prend la valeur à la deuxième ligne (la ram)
                ramLibreGB = round(float(ramLibre), 2) # arrodie et la garde à 0 chiffres après la virgule
                
                
                #cherche la RAM Totale 
                stdin, stdout, stderr = client.exec_command(r"powershell -Command (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB") #fait la commande dans la connexion SSH (retourne une tuple)
                ramTotale = stdout.read().decode() 
                ramTotaleGB = round(float(ramTotale), 2) # arrodie et la garde à 0 chiffres après la virgule
                    
        elif système == "Linux": #pour linux
            
                #cheche la RAM libre
                stdin, stdout, stderr = client.exec_command("cat /proc/meminfo | grep MemFree | awk '{print $2}'") #additionne la colonne CPU (ligne utilisateur et système) dans la commande top
                ramLibre = stdout.read().decode()
                ramIntermédiare = float(ramLibre) / 1048576.0
                ramLibreGB = round(ramIntermédiare, 2)  
                
                #cheche la RAM Totale
                stdin, stdout, stderr = client.exec_command("cat /proc/meminfo | grep MemTotal | awk '{print $2}'") #additionne la colonne CPU (ligne utilisateur et système) dans la commande top
                ramTotale = stdout.read().decode()
                ramIntermédiare = float(ramTotale) / 1048576.0
                ramTotaleGB = round(ramIntermédiare, 2)        
           
        #imprime le résultat     
        print("RAM disponible: ", ramLibreGB, "/", ramTotaleGB, " Go", sep="" )
        message = "RAM disponible :     " + str(ramLibreGB) + "/" + str(ramTotaleGB) + "Go"
        #-------------------appel pour les logs
        gestionLogs(message)
        
            
    except Exception as e:
        print("il y a eu un problème pendant la commande pour la RAM libre du client :", e)

def espaceDisqueDisponible(client, système):
    
    try:
        if système == "Windows": #pour windows
                stdin, stdout, stderr = client.exec_command('wmic logicaldisk get DeviceID, FreeSpace, Size | findstr /B "[A-Z]" | findstr /V "DeviceID"')  # cherche les disques qui commence par un lettre, et enlève la colonne qui commence par DeviceID (donc les indexes)
                disques = stdout.read().decode()
                disquesListe1 = [ligne.split() for ligne in disques.split("\n") if ligne] # if ligne (exclue les lignes qui ont rien)
                disquesListe = []
            
                for disque in disquesListe1: # enlève les disques qui ont rien comme information dedans
                    
                    if len(disque)  == 3:
                         disquesListe.append(disque)
                         
                for disque in disquesListe: # mettre en Go 
                    
                    disque[1] = float(disque[1])
                    disque[1] = disque[1] / 1073741824
                    disque[1] = round(disque[1], 2)
                    
                    disque[2] = float(disque[2])
                    disque[2] = disque[2] / 1073741824
                    disque[2] = round(disque[2], 2)  
                
                    #échange les valeurs entre la colonne 1 et 2 pour que le print de la fonction marche avec windows et linux
                    disque[1], disque[2] = disque[2], disque[1]
                
        elif système == "Linux": #pour linux
                stdin, stdout, stderr = client.exec_command("df -BG | grep '/dev/sd' | awk '{gsub(\"G\", \"\", $2); gsub(\"G\", \"\", $4); print $1, $2, $4}'") #affiche le nom, la taille totale, et l'espace restant en G(sans afficher les G) des disques montés
                disques = stdout.read().decode()
                disquesListe = [ligne.split() for ligne in disques.split("\n") if ligne] #fait une liste 2d (change de ligne quand /n)(split() pour séparer à chaque espace)
                        
        #imprime le résultat pour chaques disques
        for disque in disquesListe:
            print("Espace disques disponible: " + str(disque[0]) + " " + str(disque[2]) + "/" + str(disque[1]) + " Go", sep="")
            message = "Espace disques disponible: " + str(disque[0]) + " " +str(disque[2]) + "/" + str(disque[1]) + " Go" 
            #-------------------appel pour les logs
            gestionLogs(message)
           
    except Exception as e:
        print("il y a eu un problème pendant la commande pour l'espace disque du client :", e)
 
def listUser(client, système):
    
    try:
        if système == "Windows": #pour windows
                stdin, stdout, stderr = client.exec_command("powershell -Command (Get-LocalUser).Name") #fait la commande dans la connexion SSH (retourne une tuple)
                listeUsers = stdout.read().decode().split() # met ce qui revient en liste
                listeUsers =  ', '.join(listeUsers)
                    
        elif système == "Linux": #pour linux
                stdin, stdout, stderr = client.exec_command("awk -F ':' '{print $1}' /etc/passwd") 
                listeUsers = stdout.read().decode().split()
                listeUsers = ', '.join(listeUsers)
                      
        #imprime la liste des utilisateurs
        print("Liste Utilisateurs: ", listeUsers)
        message = f"Liste Utilisateurs   :  {listeUsers}"
        #-------------------appel pour les logs
        gestionLogs(message)
                 
    except Exception as e:
        print("il y a eu un problème pendant la commande pour la liste d'utilisateur :", e)
        
def gestionLogs(message):
    try:
        dateHeure = datetime.now().strftime("%d/%m/%Y %H:%M:%S") #met dans une variable la date et l'heure actuelle
        fichier = open("projet2machines.log", "a+", encoding="utf-8") 
        fichier.write(f"{dateHeure}     {message}\n") #écrit la date et heure actuelle ainsi que le message inscript dans la variable passée dans la fonction
        fichier.close() #ferme le fichier de log
                
    except Exception as e:
        print("erreure dans les logs :", e)
                    
def main():
    machines = cvsToDataF('machines.csv') #cvs > dataframe
    
    for lignes in range(len(machines)): #loop pour le nombre de machines indiquées dans le fichier
        machineClient = connexionSSH(machines, lignes) #connexion à la machine
        
        if machineClient == None: #si il à eu un problème à la connexion, ne fait pas les autres étapes pour cette machine, mais continue pour les autres
            continue
        
        versionOS(machineClient, machines.loc[lignes, "Type système"]) #print la version de l'os
        chargeCPU(machineClient,machines.loc[lignes, "Type système"]) #print la charge du CPU
        ramDisponible(machineClient, machines.loc[lignes, "Type système"]) #print la mémoire disponible / mémoire totale
        espaceDisqueDisponible(machineClient, machines.loc[lignes, "Type système"]) #print les disques et l'espace disponible qu'ils ont
        listUser(machineClient, machines.loc[lignes, "Type système"]) #print les utilisateurs du système

if __name__ == "__main__":
    main()
