import serial
import serial.tools.list_ports
import io
import time
import logging


class Carte():
    __arduino : serial.Serial
    __sio : io.TextIOWrapper
    __com : str
    __speed : int
    __timeout : int
    __etat : bool = False
    __num : str

    def __init__(self, com:str, speed:int, timeout:int = 1, numero : int = 0):
        self.parametrage(com, speed, timeout, numero)

    def parametrage(self, com:str, speed:int, timeout:int = 1 ,numero : int = 0)->None:
        self.__com = str(com)
        self.__speed = int(speed)
        self.__timeout = int(timeout)
        self.__num = str(numero)
        self.conexion()


    def conexion(self)->bool:
        """conecte la carte __arduino"""
        if(self.__etat==False):
            port_available = serial.tools.list_ports.comports(include_links=False)
            #print(port_available)
            if len(port_available)>0 :
                try :
                    self.__arduino = serial.Serial(self.__com, int(self.__speed), timeout = self.__timeout)
                    self.__sio = io.TextIOWrapper(io.BufferedRWPair(self.__arduino, self.__arduino))
                    self.__etat = True
                    logging.info("Carte "+str(self.__num)+" : Conecter")
                    time.sleep(2)
                except :
                    self.__etat = False
                    logging.warning("Carte "+str(self.__num)+" : Conexion Impossible")
            else:
                self.__etat = False
                logging.warning("Carte "+str(self.__num)+" : Port Inacessible")
        return(self.__etat)

    def deconnection(self)->bool:
        if(self.__etat==True):
            self.__arduino.close()
            self.__etat = False
            logging.info("Carte "+str(self.__num)+" : Deconecter")
        return(self.__etat)
    
    def send(self, data:str, no_sleep = False)->bool:
        try:
            self.__arduino.write(str(data).encode("ascii"))
            if not(no_sleep):
                time.sleep(0.01)
            logging.info("Carte "+str(self.__num)+" <-- "+str(data))
            return(True)
        except:
            logging.warning("Carte "+str(self.__num)+" : envoie de "+str(data)+" Impossible")
            return(False)
    
    def controle_moteur(self, pin:int, valeur:int, no_sleep = False)->bool:
        if(pin < 0 or pin > 13):
            logging.warning("Carte "+str(self.__num)+" pin %d invalide", pin) 
            return(False)
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (pin * 1000)
            v += valeur
            if(self.send(str(v), no_sleep)):return(True)
            else:return(False)
        return(False)

    def digitalWrite(self, pin:int, __etat:bool)->bool:
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (100000 + (pin*100) + int(__etat))
            if(self.send(str(v))): return(True)
            else: return(False)
        return(False)

    def analogRead(self, pin:int)->int:
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (110000 + pin)
            if self.send(str(v)):
                self.__sio.flush()
                result = self.__sio.readline()
                if(result >= 0 or result <= 1024): return(int(result))
        return(-1)

    def digitalRead(self, pin:int)->int:
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (120000 + pin)
            if(self.send(str(v))):
                self.__sio.flush()
                result = self.__sio.readline()
                if(result == 0 or result == 1): return(int(result))
        return(-1)
        
    def analogWrite(self, pin:int, valeur:int)->bool:
        if valeur<0 or valeur>255 : return(False)
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (200000 + (pin*1000) + valeur)
            if(self.send(str(v))): return(True)
        return(False)

    def pinMode(self, pin:int, valeur:str)->bool:
        logging.info("Carte "+str(self.__num)+" : pinMode("+str(pin)+","+str(valeur)+")")
        if valeur == "OUTPUT": val=1
        elif valeur == "INPUT": val=0
        else: return(False)
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            v = (130000 + (pin*100) + val)
            return(self.send(str(v)))

    def getState(self)->bool:
        return(self.__etat)
    
    def getSpeed(self)->bool:
        return(self.__speed)
    
    def getCom(self)->bool:
        return(self.__com)
    
    def getNum(self)->int:
        return(int(self.__num))
    
    def reset(self):
        if self.__etat == False :
            self.conexion()
        if self.__etat == True :
            self.deconnection()
            time.sleep(0.1)
            self.conexion()