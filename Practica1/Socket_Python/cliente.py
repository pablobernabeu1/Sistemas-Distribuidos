import socket
import sys
from tkinter import *


########## VENTANA ##########
ventana = Tk()
ventana.title("WhatsApp Clone with Sockets")

texto = Entry(ventana, font = ("Calibri 20"))
texto.grid(row=0, column=0, columnspan=4, padx = 10, pady = 5)

boton = Button(ventana, text="Enviar", width=5, height = 2, command = lambda: send("msg"))
boton.grid(row = 1, column = 0, padx = 0, pady = 0)

boton2 = Button(ventana, text="Recibir", width=5, height = 2, command = lambda: recibir())
boton2.grid(row = 2, column = 0, padx = 0, pady = 0)

########## CONSTANTES ##########
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
FIN = "FIN"

########## FUNCIONES ##########
def send(msg):
    msg=texto.get()
    if msg == FIN:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
        client.close()
        exit()

    else:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)

def recibir():
    respuesta = client.recv(2048).decode(FORMAT)
    texto.delete(0, END)
    texto.insert(0, respuesta)

########## MAIN ##########
if  (len(sys.argv) == 3):
    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER, PORT)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    ventana.mainloop()

    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto> <Texto Bienvenida>")






















"""
print("****** WELCOME TO OUR BRILLIANT SD UA CURSO 2020/2021 SOCKET CLIENT ****")

if  (len(sys.argv) == 3):
    SERVER = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (SERVER, PORT)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print (f"Establecida conexión en [{ADDR}]")

    msg=input()
    while msg != FIN :
        print("Envio al servidor: ", msg)
        send(msg)
        print("Recibo del Servidor: ", client.recv(2048).decode(FORMAT))
        msg=input()

    print ("SE ACABO LO QUE SE DABA")
    print("Envio al servidor: ", FIN)
    send(FIN)
    client.close()
else:
    print ("Oops!. Parece que algo falló. Necesito estos argumentos: <ServerIP> <Puerto> <Texto Bienvenida>")
"""