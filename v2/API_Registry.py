import sys
import time
import socket 
import threading
import sqlite3
from datetime import datetime


SERVER_SOCKET = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'
FIN = "FIN"

def crear_user(username, simb, passwd):
    try:
        con = sqlite3.connect('redovaland.db')
        cur = con.cursor()
        cur.execute("insert into visitantes (usrname, passwd, simbolo) values ('" + username +  "', '" + passwd + "', '" + simb + "')")

        created = con.commit()

        if created == True:
            print("Usuario creado correctamente.")
            with open("registry.log", "r+") as file:
                data = file.read()
                file.seek(0)
                file.write(str(data) + str(datetime.now()) + "; User: " + username + "; IP: " + "; Accion: crear usuario" + "; Parametros: " + passwd + ", " + simb + "\n")
                file.truncate()
            return 1
        else: 
            with open("registry.log", "r+") as file:
                data = file.read()
                file.seek(0)
                file.write(str(data) + str(datetime.now()) + "; User: " + username + "; IP: " + "; Accion: crear usuario" + "; Parametros: " + passwd + ", " + simb + "\n")
                file.truncate()
            return 0
        

    except ValueError:
        print("Error accediendo a la Base de Datos.")
        with open("registry.log", "r+") as file:
                data = file.read()
                file.seek(0)
                file.write(str(data) + "ERROR(" + str(ValueError) + "). " + str(datetime.now()) + "; User: " + username + "; IP: " + "; Accion: crear usuario" + "; Parametros: " + passwd + ", " + simb + "\n")
                file.truncate()
        print(ValueError)


def editar_user(old_username, new_username, simb, passwd):
    try:
        print("update visitantes set usrname='" + new_username + "', passwd='" + passwd + "', simbolo='" + simb + "' where usrname='" + old_username + "'")
        con = sqlite3.connect('redovaland.db')
        cur = con.cursor()

        cur.execute("update visitantes set usrname='" + new_username + "', passwd='" + passwd + "', simbolo='" + simb + "' where usrname='" + old_username + "';")
        
        con.commit()

        print("Usuario editado correctamente.")
        
        with open("registry.log", "r+") as file:
                data = file.read()
                file.seek(0)
                file.write(str(data) + str(datetime.now()) + "; User: " + old_username + "; IP: " + "; Accion: editar usuario" + "; Parametros: " + passwd + ", " + simb + "\n")
                file.truncate()

    except ValueError:
        print("Error accediendo a la Base de Datos.")
        print(ValueError)


def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")
    msg = conn.recv(1024).decode(FORMAT)
    print(f" He recibido del cliente [{addr}] el mensaje: {msg}")

    info = msg.split(" ")
    print(info)

    if info[0] == '1':
        crear_user(info[1], info[2], info[3])

    elif info[0]  == '2':
        editar_user(info[1], info[2], info[3], info[4])

    print("ADIOS. TE ESPERO EN OTRA OCASION")
    conn.close()


def start():
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER_SOCKET}")
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


########## MAIN ##########
if __name__ == "__main__":
    
    if  (len(sys.argv) == 2): # De momento se necesitan 2 argumentos hasta que se implemente el servidor de tiempos de espera.
        PORT = int(sys.argv[1]) # Almacenamos el BOOTSTRAP_SERVER para que funcione kafka.
        ADDR = (SERVER_SOCKET, PORT)

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(ADDR)
        server.bind(ADDR)

        start()
        
        
    else:
        print ("Oops!. Parece que algo falló. Necesito estos argumentos: <BOOTSTRAP_SERVER (KAFKA)> <MAX_VISITOR> <BOOTSTRAP_SERVER (FWQ_WaitingTimeServer)>")
