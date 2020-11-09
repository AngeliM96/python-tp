import random
import threading
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

cantHeladeras = 5
cantProveedores = 8
cantBeodes = 4
cantBotellasPorHeladera = 10
cantLatasPorHeladera = 15
semaforoProveedor = threading.Semaphore(1)

indiceHeladera = 0
listaHeladeras = []
botellasEnDeposito = 0
latasEnDeposito = 0
monitorBeode = threading.Condition()

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
    def tieneBotellas(self):
        return self.botellas >= 1
    def tieneLatas(self):
        return self.latas >= 1

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
            indiceHeladera += 1
                
    def cargarHeladera(self, heladera):
        global botellasEnDeposito, latasEnDeposito
        botellasAPoner = self.botellasQueTiene + botellasEnDeposito
        latasAPoner = self.latasQueTiene + latasEnDeposito
        botellasSobrantes = heladera.cargarBotellas(botellasAPoner)
        latasSobrantes = heladera.cargarLatas(latasAPoner)
        heladera.contenido()
        botellasEnDeposito += botellasSobrantes
        latasEnDeposito += latasEnDeposito

    def run(self):
        global indiceHeladera, botellasEnDeposito, latasEnDeposito
        semaforoProveedor.acquire()
        if self.hayHeladeraParaLlenar():
            self.buscarHeladera()
            heladera = listaHeladeras[indiceHeladera]
            self.cargarHeladera(heladera)
        else:
            botellasEnDeposito += self.botellasQueTiene
            latasEnDeposito += self.latasQueTiene
        semaforoProveedor.release()
   
class Beode(threading.Thread):
    def __init__(self, numero, tipoDeBebida, limite):
        super().__init__()
        self.name = f'Beode {numero + 1}'
        self.tipoDeBebida = tipoDeBebida
        self.limite = limite
        self.consumidas = 0
    def heladeraElegida(self):
        return listaHeladeras[random.randint(0, len(listaHeladeras)-1)]
    def consumirBotella(self, heladera):
        if(heladera.tieneBotellas()):
            heladera.botellas -= 1
            self.consumidas += 1
        else:
            monitorBeode.wait()
    def consumirLata(self, heladera):
        if(heladera.tieneLatas()):
            heladera.latas -= 1
            self.consumidas += 1
        else:
            monitorBeode.wait()
    def consumirAmbas(self):
        tipo = random.choice(["Lata", "Botella"])
        self.consumir(tipo)
        
    def consumir(self, tipo):
        if(tipo == "Lata"):
            self.consumirLata(self.heladeraElegida())
            logging.info(f"Tomé una lata de cerveza")
        elif(tipo == "Botella"):
            self.consumirBotella(self.heladeraElegida())
            logging.info(f"Tomé una botella de cerveza")
        else:
            self.consumirAmbas()

    def run(self):
        mensajeDeSaludoBeode = random.choice(["Como anda la vagancia?", "Buenas nocheeees", "QUE HACEEEE PABLITOOO", "Qué talco?", "Tanto tiempo che", "Hola"])
        logging.info(mensajeDeSaludoBeode)
        logging.info(f"Les aviso que mi limite es {self.limite}")
        while self.consumidas < self.limite:
            with monitorBeode:
                self.consumir(self.tipoDeBebida)
        mensajeDeDespedidaBeode = random.choice(["Vo sabe que yo te quiero a vo, no?", "Que mira gil?", "Pedime un remo no doy mas","VIVA LA PATRIA CARAJO", "MESSI EL MAS GRANDE PAPÁ"])
        logging.info(mensajeDeDespedidaBeode)
        logging.info(f"No sé qué pasó si tomé {self.consumidas} nada más")
            
for i in range(cantHeladeras):
    listaHeladeras.append(Heladera(i))

for i in range(cantProveedores):
    Proveedor(i).start()

for i in range(cantBeodes):
    limite = random.randint(2, 10)
    tipo = random.choice(["Lata", "Botella", "Ambas"])
    Beode(i, tipo, limite).start()