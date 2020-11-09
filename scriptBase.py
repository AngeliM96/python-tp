import random
import threading
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

cantHeladeras = 3
cantProveedores = 4
cantBotellasPorHeladera = 10
cantLatasPorHeladera = 15
semaforoProveedor = threading.Semaphore(1)

indiceHeladera = 0
listaHeladeras = []
botellasEnDeposito = 0
latasEnDeposito = 0

class Heladera():
    def __init__(self, numero):
        self.botellas = 0
        self.latas = 0
        self.name = f'Heladera {numero + 1}'
    def estaLlena(self):
        return self.botellas == cantBotellasPorHeladera and self.latas == cantLatasPorHeladera
    def estaVacia(self):
        return self.botellas == 0 and self.latas == 0
    def hayEspacioParaBotella(self):
        return self.botellas < cantBotellasPorHeladera
    def hayEspacioParaLata(self):
        return self.latas < cantLatasPorHeladera

    def cargarBotellas(self, botellas):
        global botellasEnDeposito
        auxBotellas = botellas
        while auxBotellas > 0:
            if self.hayEspacioParaBotella():
                self.botellas += 1
            auxBotellas -= 1
        return auxBotellas
    def cargarLatas(self, latas):
        global latasEnDeposito
        auxLatas = latas
        while auxLatas > 0:
            if self.hayEspacioParaLata():
                self.latas += 1
            auxLatas -= 1
        return auxLatas
    
    def contenido(self):
        logging.info(f"La {self.name} tiene {self.botellas} botellas y {self.latas} latas")


class Proveedor(threading.Thread):
    def __init__(self, numero):
        super().__init__()
        self.name = f'Proveedor {numero + 1}'
        # Que traigan al menos un pack, hubo veces que lo corrí y entre 5 proveedores no me llenaban una heladera
        self.botellasQueTiene = random.randint(6, 18)
        self.latasQueTiene = random.randint(6, 18)

    def hayHeladeraParaLlenar(self):
        hayHeladera = False
        for heladera in listaHeladeras:
            if not heladera.estaLlena():
                hayHeladera = True
        return hayHeladera

    def buscarHeladera(self):
        global listaHeladeras, indiceHeladera
        heladera = listaHeladeras[indiceHeladera]
        if heladera.estaLlena():
            logging.info("Enfriando las bebidas de " + heladera.name)
            indiceHeladera += 1
                
    def cargarHeladera(self, heladera):
        global botellasEnDeposito, latasEnDeposito
        botellasAPoner = self.botellasQueTiene + botellasEnDeposito
        latasAPoner = self.latasQueTiene + latasEnDeposito
        logging.info(f"Hay para cargar {botellasAPoner} botellas y {latasAPoner} latas")
        botellasSobrantes = heladera.cargarBotellas(botellasAPoner)
        latasSobrantes = heladera.cargarLatas(latasAPoner)
        heladera.contenido()
        botellasEnDeposito += botellasSobrantes
        latasEnDeposito += latasEnDeposito
        logging.info(f"En el deposito hay {botellasEnDeposito} botellas y {latasEnDeposito} latas")

    def run(self):
        global indiceHeladera, botellasEnDeposito, latasEnDeposito
        semaforoProveedor.acquire()
        if self.hayHeladeraParaLlenar():
            self.buscarHeladera()
            heladera = listaHeladeras[indiceHeladera]
            if(heladera.estaVacia()):
                logging.info("Enchufando la  "+ heladera.name)
            self.cargarHeladera(heladera)
        else:
            logging.info("Dejo las cosas en el deposito")
            botellasEnDeposito += self.botellasQueTiene
            latasEnDeposito += self.latasQueTiene
        semaforoProveedor.release()
   
    
for i in range(cantHeladeras):
    listaHeladeras.append(Heladera(i))

for i in range(cantProveedores):
    Proveedor(i).start()