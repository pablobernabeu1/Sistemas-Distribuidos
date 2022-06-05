import sys
from Auxiliar.Atraccion import Atraccion
from Auxiliar.ConsumerProducer import *
from Auxiliar.Atraccion import Atraccion
import socket
import atracciones as at

SERVER_SOCKET = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'


def almacenarTiempos(id_atraccion, numVisitantes):
    for atraccion in at.atracciones:
        if atraccion.id == id_atraccion:
            atraccion.setPersonasActuales(numVisitantes)


def leerFichero():
    try:
        with open("atraccionesWTS.txt", "r") as file:
            contenido = file.readlines()

            for atraccion in contenido:
                info = atraccion.split(" ")
                atrac = Atraccion(int(info[0]), int(info[1]), int(info[2]), int(info[3]))
                atrac.setPersonas(int(info[4]))
                at.atracciones.append(atrac)

    except:
        print("Could´t open the file.")
        return


def datosAtraccion():
    info = ""

    for atraccion in at.atracciones:
        id_atraccion = atraccion.id
        if atraccion.personasActuales == 0:
            tiempo = atraccion.tiempoPorDefecto
        
        else:
            tiempo = atraccion.personasActuales * atraccion.tiempoPorDefecto
        
        # info = "1 50 # 2 60 # 3 70 # "
        info = info + str(id_atraccion) + " " + str(tiempo) + "#"
    
    return info


def main():
    if  (len(sys.argv) == 3): # De momento se necesitan 2 argumentos hasta que se implemente el servidor de tiempos de espera.
        PORT = int(sys.argv[1])
        KAFKA_SERVER = sys.argv[2] # Almacenamos el BOOTSTRAP_SERVER para que funcione kafka.

        # SOCKETS
        ADDR = (SERVER_SOCKET, PORT)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server.bind(ADDR)

        global atracciones     

        leerFichero()
        tasks = [
            ConsumerWTS(KAFKA_SERVER),
            SocketListener(server, ADDR, SERVER_SOCKET)
        ]
        
        for t in tasks:
            t.start()
        

        
    else:
        print ("Oops!. Parece que algo falló. Necesito estos argumentos: <BOOTSTRAP_SERVER (KAFKA)> <MAX_VISITOR> <BOOTSTRAP_SERVER (FWQ_WaitingTimeServer)>")


if __name__ == "__main__":
    main()