############# Imports #############
from tkinter import *
import socket
import sys

############# Constantes #############
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
FIN = "FIN"

############# Ventana #############
ventana = Tk()
ventana.title("Calculadora Online")
############# Input #############
texto = Entry(ventana, font = ("Calibri 20"))
texto.grid(row=0, column=0, columnspan=4, padx = 10, pady = 5)