import sys
import time
import random
import socket
from Auxiliar.Atraccion import Atraccion
from Auxiliar.Visitante import Visitante
from Auxiliar.ConsumerProducer import *
import kafka
import mapa as m
import sqlite3

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
            atrac = Atraccion(row[0], row[1], row[2], row[3])
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
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        # msg = "1 50#2 60#3 70#"

        client.send("&".encode(FORMAT))
        
        msg = client.recv(1024).decode(FORMAT)
        
        info = msg.split("#") # "1 50"
        # print(info) # ['1 50', '2 60', '3 70', '']
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
                        atraccion.tiempoPorDefecto = int(tiempo)
    except:
        print("Intentando reconectar con el servidor de tiempos de espera...")

            
    for atraccion in atracciones:
        m.mapa[atraccion.fila][atraccion.col] = atraccion.tiempoPorDefecto
    
    for visitor in m.visitantes:
        if isinstance(m.mapa[visitor.posicion[0]][visitor.posicion[1]], int) == False:
            m.mapa[visitor.posicion[0]][visitor.posicion[1]] = visitor.simbolo

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

def check_user_registered(user): # Función que comprueba si un usuario está registrado, True si sí y False si no.
    global currentVisitors

    info = user.decode('utf-8')
    informacion = info.split()
    print(informacion)
    
    usrname = informacion[0]
    passwd = informacion[1]

    try:
        con = sqlite3.connect('redovaland.db')
        cur = con.cursor()

        passwdFromBD = ""
        for row in cur.execute("select passwd from visitantes where usrname='" + usrname + "'"):
            passwdFromBD = row[0]


        if passwdFromBD == passwd:
            print("El usuario " + usrname + " ha iniciado sesión correctamente con la contraseña " + passwd + "\n")
            check = True

        else:
            print("El usuario " + usrname + " ha fallado al iniciar sesión con la contraseña " + passwd + "\n")
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

        respuesta = str(numero) + " " + str(check) + " " + posicionFinal + " " + destinoFinal + " " + str(noEntrar)
        producer.send('respuestaComprobarUsuario', respuesta.encode(FORMAT))
        producer.close()

        if check:
            currentVisitors += 1
            visitor = obtenerVisitorByUsrname(usrname, destino, int(numero))
            m.visitantes.append(visitor)


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
    
