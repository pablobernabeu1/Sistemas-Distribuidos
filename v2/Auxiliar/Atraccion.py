class Atraccion():
    def __init__(self, id, fila, col, tiempoPorDefecto, sector):
        self.id = id
        self.fila = fila
        self.col = col
        self.tiempoPorDefecto = tiempoPorDefecto
        self.numeroPersonasMax = 0
        self.personasActuales = 0
        self.sector = sector

    def setPersonas(self, n):
        self.numeroPersonasMax = n

    def setPersonasActuales(self, n):
        self.personasActuales = n
        
    def setSector(self, s):
        self.sector = s