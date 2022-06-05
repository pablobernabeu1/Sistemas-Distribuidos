import sys
from Auxiliar.Atraccion import Atraccion
from Auxiliar.ConsumerProducer import *


if __name__ == "__main__":
    
    if  (len(sys.argv) == 3): # De momento se necesitan 2 argumentos hasta que se implemente el servidor de tiempos de espera.
        KAFKA_SERVER = sys.argv[1] # Almacenamos el BOOTSTRAP_SERVER para que funcione kafka.
        ID_ATRACCION = int(sys.argv[2])

        tasks = [
            ProducerSensor(KAFKA_SERVER, ID_ATRACCION),
            ProducerSensor2(KAFKA_SERVER, ID_ATRACCION),
        ]
        
        for t in tasks:
            t.start()
        

        
    else:
        print ("Oops!. Parece que algo falló. Necesito estos argumentos: <BOOTSTRAP_SERVER (KAFKA)> <MAX_VISITOR> <BOOTSTRAP_SERVER (FWQ_WaitingTimeServer)>")