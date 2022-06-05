import threading, time
import kafka
import FWQ_Visitor as vis
import FWQ_Engine as eng
import random
import os
import mapa as m
import FWQ_WaitingTimeServer as wts
import atracciones as at
import socket
import pyaes


FORMAT = 'utf-8'

############### AUXILIAR ###############

def start(server, SERVER_SOCKET):
    server.listen()
    print(f"[LISTENING] Servidor a la escucha en {SERVER_SOCKET}")
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


def start2(server, SERVER_SOCKET, visitors):
    server.listen()
    while True:
        conn, addr = server.accept()
        CONEX_ACTIVAS = threading.active_count()
        thread = threading.Thread(target=handle_client2, args=(conn, addr, visitors))
        thread.start()


def handle_client(conn, addr):
    print(f"[NUEVA CONEXION] {addr} connected.")
    msg = conn.recv(1024).decode(FORMAT)
    print(f" He recibido del cliente [{addr}] el mensaje: {msg}")

    # "&"

    info = wts.datosAtraccion()
    # print(info)
    # print(eng.devolverVisitantes())
    conn.send(info.encode(FORMAT))

    print("ADIOS. TE ESPERO EN OTRA OCASION")
    conn.close()


def handle_client2(conn, addr, visitors):
    token = conn.recv(1024).decode(FORMAT)
    # "&"

    info = ""
    for visitor in visitors:
        if int(visitor.token) == int(token):
            info = str(visitor.posicion[0]) + " " + str(visitor.posicion[1]) + " " + str(visitor.destino[0]) + " " + str(visitor.destino[1])

    conn.send(info.encode(FORMAT))
    conn.close()

############### ENGINE ###############

# Consumidor que recibe las solicitudes de los visitantes
class ConsumerEngine(threading.Thread):
    def __init__(self, KAFKA_SERVER):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = kafka.KafkaConsumer('comprobarUsuario', bootstrap_servers = self.server, auto_offset_reset='latest')

        while not self.stop_event.is_set():
            for message in consumer:
                info = message.value
                try:
                    info = info.decode() # str
                    informacion = info.split()
                    
                    numero = informacion[2]
                    
                except:
                    numero = 0
                
                eng.check_user_registered(message.value, numero)
                if self.stop_event.is_set():
                    break

        consumer.close()

# Consumidor que recibe los movimientos de los visitantes <----
class ConsumerEngineMovimientosVisitante(threading.Thread):
    def __init__(self, KAFKA_SERVER):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = kafka.KafkaConsumer('enviarMovimiento', bootstrap_servers = self.server, auto_offset_reset='latest')

        while not self.stop_event.is_set():
            for message in consumer:
                informacion = message.value.decode("ISO-8859-1")
                # DECODIFICAR
                
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
                            informacionDesencriptada = aes.decrypt(informacion)
                            informacion = informacionDesencriptada
                
                    except:
                        print("El visitante no ha enciptado el canal.")
                    
                
                # Lógica para recibir los movimientos de los visitantes y actualizar el mapa
                
                info = informacion.split()
                try:
                    eng.cambiarPosicionVisitantes(int(info[0]), int(info[1]), int(info[2]))
                    visitors = eng.devolverVisitantes()
                    atracs = eng.devolverAtracciones()
                    
                    for visitor in visitors:
                        if visitor.posicion == visitor.destino:
                            tiempoAux = 10000
                            for atrac in atracs:
                                if atrac.tiempoPorDefecto < tiempoAux:
                                    atraccionConMenorTiempo = atrac
                                    tiempoAux = atrac.tiempoPorDefecto

                            newTuple = (atraccionConMenorTiempo.fila, atraccionConMenorTiempo.col)
                            visitor.destino = newTuple
                    
                    if self.stop_event.is_set():
                        break
                except:
                    continue

        consumer.close()

# Productor que envia el mapa a los visitantes loggeados
class ProducerEngine(threading.Thread):
    def __init__(self, KAFKA_SERVER, ADDR):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER
        self.addr = ADDR

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = kafka.KafkaProducer(bootstrap_servers=self.server)

        while not self.stop_event.is_set():
            m.mapa = eng.cambiar_mapa(m.mapa, self.addr)
            
            # eng.guardarMapa(m.visitantes, eng.devolverAtracciones())
            producer.send('enviarMapa', eng.mapaToString(m.mapa).encode(FORMAT))
            time.sleep(2)

        producer.close()

# Producer que envia los nuevos destinos a los visitantes
class ProducerEngineEnviarNuevoDestino(threading.Thread):
    def __init__(self, KAFKA_SERVER):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while True:
            try:
                ADDR = ("127.0.1.1", 5555)
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.bind(ADDR)
                visitors = eng.devolverVisitantes()
                start2(server, "127.0.1.1", visitors)
            except:
                continue

##############################

############### SENSOR Y WTS ###############

# Productor que envia las personas al WTS
class ProducerSensor(threading.Thread):
    def __init__(self, KAFKA_SERVER, id_atrac):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER
        self.id_atraccion = id_atrac

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = kafka.KafkaProducer(bootstrap_servers=self.server)

        while not self.stop_event.is_set():
            valores = (1, 2, 3)
            valorRandom = random.randint(0, 2)
            numeroVisitantes = valores[valorRandom]

            info = str(self.id_atraccion) + " " + str(numeroVisitantes)
            producer.send('enviarSensor', info.encode(FORMAT))

            time.sleep(20)
            
        producer.close()
        
# Productor que envia las personas al WTS
class ProducerSensor2(threading.Thread):
    def __init__(self, KAFKA_SERVER, id_atrac):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER
        self.id_atraccion = id_atrac

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = kafka.KafkaProducer(bootstrap_servers=self.server)

        while not self.stop_event.is_set():
            numeroVisitantes = 0
            numeroVisitantes = input("Introduce el número de visitantes: ")

            info = str(self.id_atraccion) + " " + str(numeroVisitantes)
            producer.send('enviarSensor', info.encode(FORMAT))

            
        producer.close()

# Consumidor que recibe los tiempos de los sensores
class ConsumerWTS(threading.Thread):
    def __init__(self, KAFKA_SERVER):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = kafka.KafkaConsumer('enviarSensor', bootstrap_servers = self.server, auto_offset_reset='latest')

        while not self.stop_event.is_set():
            for message in consumer:
                informacion = message.value.decode(FORMAT)

                info = informacion.split()

                wts.almacenarTiempos(int(info[0]), int(info[1]))

                if self.stop_event.is_set():
                    break

        consumer.close()


class SocketListener(threading.Thread):
    def __init__(self, serv, ad, sock):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = serv
        self.addr = ad
        self.sock = sock

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.server.bind(self.addr)

        start(self.server, self.sock)

##############################

############### VISITORS ###############

# Consumidor que recibe el mapa
class ConsumerVisitor(threading.Thread):
    def __init__(self, KAFKA_SERVER):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = kafka.KafkaConsumer('enviarMapa', bootstrap_servers = self.server, auto_offset_reset='latest')

        while not self.stop_event.is_set():
            for message in consumer:
                os.system("clear")
                vis.mostrarMapa(vis.mapaToMatrix(message.value.decode(FORMAT)))

                if self.stop_event.is_set():
                    break

        consumer.close()

# Productor que envia su nueva posicion al Engine
class ProducerVisitor(threading.Thread):
    def __init__(self, KAFKA_SERVER, tok):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()
        self.server = KAFKA_SERVER
        self.token = tok

    def stop(self):
        self.stop_event.set()

    def run(self):
        producer = kafka.KafkaProducer(bootstrap_servers=self.server)

        while not self.stop_event.is_set():
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ADDR = ("127.0.1.1", 5555)
            client.connect(ADDR)

            info = str(self.token)
            client.send(info.encode(FORMAT))
            msg = client.recv(1024).decode(FORMAT)
            info = msg.split()

            posicionActual = (int(info[0]), int(info[1]))
            destino = (int(info[2]), int(info[3]))

            # Coordenada x
            if destino[0] > posicionActual[0]:
                newTuple = posicionActual[0] + 1 , posicionActual[1]
                posicionActual = newTuple
            elif destino[0] < posicionActual[0]:
                newTuple = posicionActual[0] - 1 , posicionActual[1]
                posicionActual = newTuple

            # Coordenada y
            if destino[1] > posicionActual[1]:
                newTuple = posicionActual[0] , posicionActual[1] + 1
                posicionActual = newTuple

            elif destino[1] < posicionActual[1]:
                newTuple = posicionActual[0] , posicionActual[1] - 1
                posicionActual = newTuple

            time.sleep(1)
            info = str(posicionActual[0]) + " " + str(posicionActual[1]) + " " + str(self.token) 
            
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
                        key = id_aes.encode('utf-8')
                        
                        aes = pyaes.AESModeOfOperationCTR(key)
                        informacion = info
                        
                        info = aes.encrypt(informacion)

                except:
                    print("No se pudo leer el fichero con la clave compartida.")
                
            else:
                info = info.encode()
            
            producer.send('enviarMovimiento', info)

        producer.close()

# Visitante para salir del mapa
class SalirDelParque(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        salir = input()
        quit("Todo bien")
        
        
##############################
