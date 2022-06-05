FUNCIONAMIENTO DE LA APLICACIÓN

TERMINAL:
    cd /Practica1SD/kafka x3
    - zookeeper-server-start config\zookeeper.properties <- Iniciar zookeeper
    - kafka-server-start config\server.properties <- Iniciar kafka
    - zookeeper-server-stop <- Parar kafka
    - kafka-console-producer --bootstrap-server localhost:9092 --topic TOPIC <- Crear un nuevo tópico
    - kafka-topics --bootstrap-server localhost:9092 -list <- Listar los tópicos

    - CLASE:

        - .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
        - .\bin\windows\kafka-server-start.bat .\config\server.properties

        LINUX:

            cambiar rutas de zookeeper.properties y server.properties
            - ./bin/zookeeper-server-start.sh ./config/zookeeper.properties
            - ./bin/kafka-server-start.sh ./config/server.properties
            pip install kafka
            pip install kafka-python


EJECUTAR LA APLICACION:

    python3 ./FWQ_Engine.py localhost:9092 20 127.0.1.1 6969
    python3 ./API_Registry.py 6666
    python3 ./API_Visitante.py 127.0.1.1 6666 localhost:9092
    python3 ./FWQ_Sensor.py localhost:9092 1 // python3 ./FWQ_Sensor.py localhost:9092 2 // python3 ./FWQ_Sensor.py localhost:9092 3 
    python3 ./FWQ_Sensor.py localhost:9092 4 // python3 ./FWQ_Sensor.py localhost:9092 5 // python3 ./FWQ_Sensor.py localhost:9092 6 
    python3 ./FWQ_WaitingTimeServer.py 6969 localhost:9092


NUEVOS:

.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

.\bin\windows\kafka-server-start.bat .\config\server.properties