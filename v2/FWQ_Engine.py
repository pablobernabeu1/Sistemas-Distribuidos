import sys
import time
import random
import socket

from requests import api
from Auxiliar.Atraccion import Atraccion
from Auxiliar.Visitante import Visitante
from Auxiliar.ConsumerProducer import *
import kafka
import mapa as m
import sqlite3
import requests
import json
import pyaes

# Variable global que guarda el numero de visitantes en el parque
currentVisitors = 0

# Lista que guarda los visitantes actuales del parque
atracciones = []

puerta1Fila = 0
puerta1Col = 0

FORMAT = 'utf-8'

# Funciones auxiliar

def guardarMapa(visitantes, atracciones):
    try:
        print()
    
    except:
        print("Error accediendo a la Base de Datos.")

def devolverAtracciones():
    return atracciones

def devolverVisitantes():
    return m.visitantes
        
def obtener_atracciones():
    try:
        con = sqlite3.connect('redovaland.db')
        cur = con.cursor()
        atraccioness = []
        for row in cur.execute("select * from atracciones"):
            atrac = Atraccion(row[0], row[1], row[2], row[3], int(row[4]))
            atraccioness.append(atrac)

        return atraccioness

    except: 
        print("Error de conexión con la base de datos.")

def obtener_atraccion_menor_tiempo(atracciones):
    menorTiempo = 1000
    for a in atracciones:
        if a.tiempoPorDefecto < menorTiempo:
            menorTiempo = a.tiempoPorDefecto
            atraccion = a

    return atraccion

def crear_mapa():
    mapa = []
    global atracciones

    for i in range(20):
        mapa.append([])
        for j in range(20):
            mapa[i].append(".")

    
    atraccioness = obtener_atracciones()

    for a in atraccioness:
        mapa[a.fila][a.col] = a.tiempoPorDefecto
        atracciones.append(a)


    return mapa

def cambiar_mapa(mapa, ADDR):
    ############################## OPEN WEATHER ##############################
    listaCiudades = list()
    
    try:
        with open("ciudades.txt", "r") as file:
            contenido = file.readlines()
            for ciudad in contenido:
                listaCiudades.append(str(ciudad))
        
    except:
        print("No se pudo leer el archivo de ciudades.")
        
    
    try:
        with open("openWeather.txt", "r") as file:
            contenido = file.readlines()
            for ciudad in contenido:
                api_url = str(ciudad)
        
    except:
        print("No se pudo leer el archivo de OpenWeather.")
        
    api_url_ok = "http://api.openweathermap.org/data/2.5/weather?q="
    
    
    aux1 = False
    aux2 = False
    aux3 = False
    aux4 = False
    
    url_ok = False
    if api_url == api_url_ok:
        url_ok = True
        api_key = "2ce2affb59c6e8102bbc3543fa18e4ea"
        url1 = api_url + listaCiudades[0] + "&appid=53c6ca4afb5fd23a2d552de70d029b5f"
        url2 = api_url + listaCiudades[1] + "&appid=53c6ca4afb5fd23a2d552de70d029b5f"
        url3 = api_url + listaCiudades[2] + "&appid=53c6ca4afb5fd23a2d552de70d029b5f"
        url4 = api_url + listaCiudades[3] + "&appid=53c6ca4afb5fd23a2d552de70d029b5f"
        
        ########################## SECTOR 1 ##########################
        aux1 = False
        # Realizamos la petición
        try:
            response = requests.get(url1)
            # Obtenenemos el json
            data = json.loads(response.text) 
            # Obtenemos la temperatura
            temp1 = int(data["main"]["temp"]) 
            # Conevertimos a grados centigrados
            temp1 = temp1 - 273.15 
            if temp1 < 20 or temp1 > 30:
                aux1 = True # Se pone un '!'
                
        except requests.exceptions.ConnectionError:
            print("Conexion rechazada.")
            aux1 = False
        
            
        ########################## SECTOR 2 ##########################
        aux2 = False
        # Realizamos la petición
        try:
            response = requests.get(url2)
            # Obtenenemos el json
            data = json.loads(response.text) 
            # Obtenemos la temperatura
            temp2 = int(data["main"]["temp"]) 
            # Conevertimos a grados centigrados
            temp2 = temp2 - 273.15 
            if temp2 < 20 or temp2 > 30:
                aux2 = True # Se pone un '!'
                
        except requests.exceptions.ConnectionError:
            print("Conexion rechazada.")
            aux2 = False
        
            
        ########################## SECTOR 3 ##########################
        aux3 = False
        # Realizamos la petición
        try:
            response = requests.get(url3)
            # Obtenenemos el json
            data = json.loads(response.text) 
            # Obtenemos la temperatura
            temp3 = int(data["main"]["temp"]) 
            # Conevertimos a grados centigrados
            temp3 = temp3 - 273.15 
            if temp3 < 20 or temp3 > 30:
                aux3 = True # Se pone un '!'
                
        except requests.exceptions.ConnectionError:
            print("Conexion rechazada.")
            aux3 = False
        
            
        ########################## SECTOR 4 ##########################
        aux4 = False
        # Realizamos la petición
        try:
            response = requests.get(url4)
            # Obtenenemos el json
            data = json.loads(response.text) 
            # Obtenemos la temperatura
            temp4 = int(data["main"]["temp"]) 
            # Conevertimos a grados centigrados
            temp4 = temp4 - 273.15 
            if temp4 < 20 or temp4 > 30:
                aux4 = True # Se pone un '!'
                
        except requests.exceptions.ConnectionError:
            print("Conexion rechazada.")
            aux4 = False
        
            
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        # msg = "1 50#2 60#3 70#"

        client.send("&".encode(FORMAT))
        
        msg = client.recv(1024).decode(FORMAT)
        
        info = msg.split("#") # "1 50"
        for elem in info:
            if elem != '':
                id_atraccion = elem[0]
                if len(elem) == 4:
                    tiempo = str(elem[2]) + str(elem[3])
                elif len(elem) == 5:
                    tiempo = str(elem[2]) + str(elem[3]) + str(elem[4])
                else:
                    tiempo = str(elem[2])
                
                for atraccion in atracciones:
                    if atraccion.id == int(id_atraccion):
                        if atraccion.sector == 1 and aux1 == True:
                            atraccion.tiempoPorDefecto = 404
                        elif atraccion.sector == 2 and aux2 == True:
                            atraccion.tiempoPorDefecto = 404
                        elif atraccion.sector == 3 and aux3 == True:
                            atraccion.tiempoPorDefecto = 404
                        elif atraccion.sector == 4 and aux4 == True:
                            atraccion.tiempoPorDefecto = 404
                        else:  
                            atraccion.tiempoPorDefecto = int(tiempo)
    except:
        print("Intentando reconectar con el servidor de tiempos de espera...")

            
    for atraccion in atracciones:
        if url_ok == False:
                m.mapa[atraccion.fila][atraccion.col] = "?"
                
        elif atraccion.tiempoPorDefecto == 404:
            m.mapa[atraccion.fila][atraccion.col] = "!"
                
        else:
            m.mapa[atraccion.fila][atraccion.col] = atraccion.tiempoPorDefecto
    
    for visitor in m.visitantes:
        if isinstance(m.mapa[visitor.posicion[0]][visitor.posicion[1]], int) == False:
            m.mapa[visitor.posicion[0]][visitor.posicion[1]] = visitor.simbolo
            
    
    # Guardar el mapa en la base de datos
    try:
        with open("mapa.txt", "w") as file:
            file.write(mapaToString2(m.mapa))
        
    except:
        print("No se pudo escribir el mapa en la BBDD.")
        
    return mapa

def mapaToString(mapa):
    cadena = "#"
    cadena += "\n\n********** RedovaLand Activity Map **********\n"
    cadena += "ID\tNombre\t\tSimbolo\t\tPosicion\tDestino\n"

    for personaje in m.visitantes:
        posicion = str(personaje.posicion[0]) + ", " + str(personaje.posicion[1])
        destino = str(personaje.destino[0]) + ", " + str(personaje.destino[1])
        cadena = cadena + str(personaje.id) + "\t" + personaje.usrname + "\t\t" + personaje.simbolo + "\t\t" + posicion + "\t\t" + destino + "\n"

    cadena += "#"

    for row in range(20):
        for col in range (20):
            cadena = cadena + " " + str(mapa[row][col])
        cadena = cadena + " |"

    return cadena

def mapaToString2(mapa):
    cadena = ""
    cadena += "********** RedovaLand Activity Map **********<br/>"
    cadena += "ID&emsp;Nombre&emsp;&emsp;Simbolo&emsp;&emsp;Posicion&emsp;Destino<br/>"

    for personaje in m.visitantes:
        posicion = str(personaje.posicion[0]) + ", " + str(personaje.posicion[1])
        destino = str(personaje.destino[0]) + ", " + str(personaje.destino[1])
        cadena = cadena + str(personaje.id) + "&emsp;&emsp;&nbsp;" + personaje.usrname + "&emsp;&emsp;&nbsp;" + personaje.simbolo + "&emsp;&emsp;&emsp;&emsp;&emsp;" + posicion + "&emsp;&emsp;&emsp;" + destino + "<br/>"

    for row in range(20):
        for col in range (20):
            cadena = cadena + " " + str(mapa[row][col])
        cadena = cadena + "<br/>"

    return cadena

def cambiarPosicionVisitantes(newFila, newCol, token):
    for visitor in m.visitantes:
        if int(visitor.token) == int(token):
            m.mapa[visitor.posicion[0]][visitor.posicion[1]] = "."
            newTuple = newFila, newCol
            visitor.posicion = newTuple

# Funciones principales
def obtenerVisitorByUsrname(usrname, destino, token):
    try:
        con = sqlite3.connect('redovaland.db')
        cur = con.cursor()

        for row in cur.execute("select * from visitantes where usrname='" + usrname + "'"):
            puertaAux = puerta1Fila , puerta1Col
            visitor = Visitante(row[0], row[1], row[2], row[3], puertaAux, destino, int(token)) # Creamos el visitante

        return visitor

    except ValueError:
        print("Error accediendo a la Base de Datos.")
        print(ValueError)

def check_user_registered(user, numeroAux): # Función que comprueba si un usuario está registrado, True si sí y False si no.
    global currentVisitors
    noEncriptado = False
    
    info = user # bytes
    
    ###################### Securización del canal ######################
    try:
        with open("flagEngine.txt", "r") as file:
            contenido = file.readlines()
            flag = int(contenido[0])
        
    except:
        print("No se pudo abrir el fichero con el flag.")
        
    if flag == 1:
        try:
            with open("id_aes.txt", "r") as file:
                contenido = file.readlines()
                id_aes = str(contenido[0])
                key = id_aes.encode('utf-8')
                aes = pyaes.AESModeOfOperationCTR(key)

                informacionDesencriptada = aes.decrypt(info)
                
                print("Hay que desencriptar.")
                print(info)
                print(informacionDesencriptada)
                info = informacionDesencriptada
    
        except:
            print("El visitante no ha enciptado el canal.")
                    
    else:
        print("No hay que desencriptar")
        print(info) # bytes
        
    try:
        info = info.decode() # str
        informacion = info.split()
        print(informacion)
        
        usrname = str(informacion[0])
        passwdEncrypted = str(informacion[1])
        
    except:
        noEncriptado = True

    try:
        if noEncriptado == False:
            con = sqlite3.connect('redovaland.db')
            cur = con.cursor()

            passwdFromBD = ""
            for row in cur.execute("select passwd from visitantes where usrname='" + usrname + "'"):
                passwdFromBD = row[0]


            if passwdFromBD == passwdEncrypted:
                print("El usuario " + usrname + " ha iniciado sesión correctamente con la contraseña " + passwdEncrypted + "\n")
                check = True

            else:
                print("El usuario " + usrname + " ha fallado al iniciar sesión con la contraseña " + passwdEncrypted + "\n")
                check = False

            
            producer = kafka.KafkaProducer(bootstrap_servers="localhost:9092")
            numero = informacion[2]

            # Obtenemos la informacion sobre la posicion inicial y el destino del visitante

            atraccion = obtener_atraccion_menor_tiempo(obtener_atracciones()) # Obtenemos la atraccion con menor tiempo de espera
            destino = (atraccion.fila, atraccion.col) # A partir de esa atraccion obtenida formamos una tupla con su fila y columna

            posicionFinal = str(puerta1Fila) + " " + str(puerta1Col)
            destinoFinal = str(destino[0]) + " " + str(destino[1])

            noEntrar = False
            if currentVisitors + 1 > m.MAX_VISITOR:
                noEntrar = True
                
            producer = kafka.KafkaProducer(bootstrap_servers="localhost:9092")
            respuesta = str(numero) + " " + str(check) + " " + posicionFinal + " " + destinoFinal + " " + str(noEntrar) + " " + str(noEncriptado)
            producer.send('respuestaComprobarUsuario', respuesta.encode(FORMAT))
            producer.close()
            
            if check:
                currentVisitors += 1
            visitor = obtenerVisitorByUsrname(usrname, destino, int(numero))
            m.visitantes.append(visitor)
            
        else:
            numero = numeroAux
            check = True
            posicionFinal = "1 2"
            destinoFinal = "1 2"
            noEntrar = False
            
            producer = kafka.KafkaProducer(bootstrap_servers="localhost:9092")
            respuesta = str(numero) + " " + str(check) + " " + posicionFinal + " " + destinoFinal + " " + str(noEntrar) + " " + str(noEncriptado)
            producer.send('respuestaComprobarUsuario', respuesta.encode(FORMAT))
            producer.close()


    except ValueError:
        print("Error accediendo a la Base de Datos.")
        print(ValueError)
    

def main():
    if  (len(sys.argv) == 5): # De momento se necesitan 2 argumentos hasta que se implemente el servidor de tiempos de espera.
        KAFKA_SERVER = sys.argv[1] # Almacenamos el BOOTSTRAP_SERVER para que funcione kafka.
        m.MAX_VISITOR = int(sys.argv[2])
        SERVER = sys.argv[3]
        PORT = int(sys.argv[4])

        ADDR = (SERVER, PORT)

        m.mapa = eng.crear_mapa()
        tasks = [
            ConsumerEngine(KAFKA_SERVER), # Consumidor que recibe a los usuarios, los verifica y los añade al array.
            ProducerEngine(KAFKA_SERVER, ADDR), # Productor que envia el mapa a los usuarios
            ConsumerEngineMovimientosVisitante(KAFKA_SERVER), # Consumer que recibe los movimientos de los visitors y actualiza su posicion en el mapa.
            ProducerEngineEnviarNuevoDestino(KAFKA_SERVER),
        ]

        for t in tasks:
            t.start()

        
    else:
        print ("Oops!. Parece que algo falló. Necesito estos argumentos: <BOOTSTRAP_SERVER (KAFKA)> <MAX_VISITOR> <BOOTSTRAP_SERVER (FWQ_WaitingTimeServer)>")

########## MAIN ##########
if __name__ == "__main__":
    main()
    
