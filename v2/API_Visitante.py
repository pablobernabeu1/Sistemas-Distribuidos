import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

import sys
import kafka
import socket
import random
import os
import time
from Auxiliar.ConsumerProducer import *
import hashlib
import pyaes
import getpass
import requests

FORMAT = 'utf-8'

# Función auxiliar
def mapaToMatrix(mapa):
    resultado = []
    resultado.append([])
    filas = 0

    cabecera = "" # Variable para almacenar la cabecera del mapa
    fin = 0 # Variable que guarda en que posicion termina la cabecera
    aux = 0 # Variable que indica cuando termina la cabecera del mapa
    cont = 0 # Variable que cuenta todos los caracteres recorridos
    for x in mapa:
        if x == "#":
            aux += 1

        if aux == 2:
            fin = cont
            break

        cabecera += x
        cont += 1

    mapa2 = mapa[fin + 1: len(mapa)]

    for i in mapa2:
        if i == "|":
            if filas != 19:
                filas += 1
                resultado.append([])

        elif i != " " and i != "|":
            resultado[filas].append(str(i))
        
    return cabecera, resultado


def mostrarMapa(tupla): 
    cabecera = tupla[0]
    print(cabecera)

    mapa = tupla[1]
    for row in range(20):
        cadena = ""
        for col in range(20):
            cadena = cadena + " " + str(mapa[row][col])

        print(cadena)


def dentro_del_parque(token): # Función para cuando el usuario haya entrado al parque.
    tasks = [
        ConsumerVisitor("localhost:9092"),
        ProducerVisitor("localhost:9092", token),
        SalirDelParque(),
    ]

    
    for t in tasks:
        t.start()


def menu_principal(ADDR):
    finished = False
    while(finished!=True):
        print("\n¡¡Bienvenido a RedovanLand!!")
        print("1. Crear perfil.")
        print("2. Editar perfil.")
        print("3. Entrar al parque.")
        print("4. Salir.")

        opt = int(input("\nSeleccione una opción (1/2/3/4): "))

        if opt == 1:
            username = input("Nombre de usuario: ").encode()
            simb = input("Eliga un simbolo que le represente: ").encode() 
            passwd = getpass.getpass("Contraseña: ").encode() # Que no aparezca la contraseña
            
            EncryptedPasswd = hashlib.sha256(passwd)
            EncryptedPasswd = EncryptedPasswd.hexdigest().encode()
            
            # CIFRADO --- ENCODE - DECODE
            
            with open("public_shared.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            
            # USERNAME
            encryptedUsername = public_key.encrypt(
                username,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # SIMBOLO
            encryptedSimbolo = public_key.encrypt(
                simb,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            # PASSWD
            EncryptedPasswdRSA = public_key.encrypt(
                EncryptedPasswd,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            try: 
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                
                encryptedUsername = encryptedUsername.decode("iso-8859-1")
                encryptedSimbolo = encryptedSimbolo.decode("iso-8859-1")
                EncryptedPasswdRSA = EncryptedPasswdRSA.decode("iso-8859-1")
                
                response = requests.post("http://127.0.1.1:4000/crearusuario", json={"username": str(encryptedUsername), "simbolo": str(encryptedSimbolo), "passwd": str(EncryptedPasswdRSA)})
                print(response.text)
                
            except:
                print("Módulo Registry no está activa.")         
            
        elif opt == 2:
            old_username = input("Nombre de usuario anterior: ")
            new_username = input("Nuevo nombre de usuario: ")
            simb = input("Nuevo simbolo que le represente: ")
            passwd = getpass.getpass("Contraseña: ") # Que no aparezca la contraseña
            passwd = passwd.encode('utf-8')
            
            EncryptedPasswd = hashlib.sha256(passwd)
            EncryptedPasswd = EncryptedPasswd.hexdigest()

            try: 
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                
                response = requests.post("http://127.0.1.1:4000/editarusuario?oldusrname=" + str(old_username) + "&newusrname=" + new_username + "&simbolo=" + str(simb) + "&passwd=" + str(EncryptedPasswd))
                print(response.text)
                
            except:
                print("Módulo Registry no está activa.")  

        elif opt == 3:
            username = input("Username: ")
            passwd = getpass.getpass("Contraseña: ") # Que no aparezca la contraseña
            passwd = passwd.encode()
            
            numeroRandom = random.randint(0, 500000000)

            EncryptedPasswd = hashlib.sha256(passwd)
            EncryptedPasswd = EncryptedPasswd.hexdigest() # str
            
            ###################### Securización del canal ######################
            try:
                with open("flagVisitante.txt", "r") as file:
                    contenido = file.readlines()
                    flag = int(contenido[0])
                
            except:
                print("No se pudo abrir el fichero con el flag.")
                
            
            if flag == 1:
                try:
                    with open("id_aes.txt", "r") as file:
                        contenido = file.readlines()
                        id_aes = str(contenido[0])
                        key = id_aes.encode()
                        
                        aes = pyaes.AESModeOfOperationCTR(key)
                        informacion = username + " " + EncryptedPasswd + " " + str(numeroRandom)
                        
                        info = aes.encrypt(informacion) # bytes
                
                except:
                    print("No se pudo leer el fichero con la clave compartida.")
                    
            else:
                info = username + " " + str(EncryptedPasswd) + " " + str(numeroRandom)
                info = info.encode() # bytes
                
            producer = kafka.KafkaProducer(bootstrap_servers=KAFKA_SERVER) # Creamos un producer en el visitor para enviar su información.
            producer.send('comprobarUsuario', info)
            consumer = kafka.KafkaConsumer('respuestaComprobarUsuario', bootstrap_servers="localhost:9092", auto_offset_reset='earliest')
            
            for msg in consumer:
                respuesta = msg.value.decode(FORMAT)
                informacion = respuesta.split()
                noEntrar = False
                noEntrar = informacion[6] 
                noEncriptado = informacion[7]
                
                if noEntrar == "True" and informacion[0] == str(numeroRandom):
                    print("Lo sentimos, RedovaLand está con aforo máximo. Le esperamos en otra ocasión.")
                    exit()
                
                posicionActual = int(informacion[2].replace(',', '')) , int(informacion[3])
                destino = int(informacion[4].replace(',', '')) , int(informacion[5])

                if informacion[0] == str(numeroRandom):
                    consumer.close()
                    
                
            if noEncriptado == "True":
                print("Lo sentimos, RedovaLand está teniendo problemas de seguridad.")
                exit()
            
            if str(numeroRandom) == informacion[0] and informacion[1] == "True":
                print("\n¡¡ Has entrado en el parque !!")
                dentro_del_parque(int(numeroRandom))

            elif informacion[1] == "False":
                print("Contraseña incorrecta.") 
            
        elif opt == 4:
            print("Adiós. Que pase un buen día:)")
            finished = True

        else:
            print("Opción incorrecta.")


########## MAIN ##########
if __name__ == "__main__":
    
    if  (len(sys.argv) == 4):
        SERVER = sys.argv[1]
        PORT = int(sys.argv[2])
        KAFKA_SERVER = sys.argv[3]
        ADDR = (SERVER, PORT)

        menu_principal(ADDR)

    else:
        print ("Oops!. Parece que algo falló. Necesito estos argumentos: <BOOTSTRAP_SERVER (KAFKA)> <MAX_VISITOR> <BOOTSTRAP_SERVER (FWQ_WaitingTimeServer)>")

