from robot.arduino import Carte
import json
import logging
import time
import random
import numpy as np

class Moteur():
    __min : int
    __max : int
    __pin : int
    __speed : int
    __arduino : Carte
    __position : int = 50
    __i : int = 0
    __action = []
    name : str
    
    def __init__(self, min_, max_, pin, carte,speed, nom='') -> None:
        self.name = str(nom)
        self.__setMin(min_)
        self.__setMax(max_)
        self.setPin(pin)
        self.__arduino = carte
        self.__speed = speed

    def __setMin(self, min_)->None:
        if(min_ >= 0 and min_ <= 180): self.__min=min_
        else: 
            logging.error("Motteur "+str(self.name)+" : min is not in range [0, 180]")

    def __setMax(self, max_)->None:
        if(max_>=0 and max_<=180): self.__max=max_
        else: 
            logging.error("Motteur "+ str(self.name) +" : max is not in range [0, 180]")

    def setPin(self, pin)->None:
        if(pin>=0 and pin<=13):
            self.__pin=pin
        else:
            logging.error("Motteur "+str(self.name)+" : pin is not in range [0, 13]")
    
    def __proportionel(self, val:float)->int:
        """val en % du mouvement"""
        return(int((val/100)*(self.__max - self.__min )+self.__min))
    
    def setCarte(self, carte:Carte)->None:
        self.__arduino = carte
    
    def move(self, position:float)->None:
        print('move pin :', self.__pin, '  ', position)
        #if(position < self.__position + 1 and position > self.__position-1): return False
        if position == self.__position : return False
        print("deplacement du moteur " + str(self.name) + " à la position : " + str(self.__position))
        self.stop()
        self.__action.append(True)
        i = self.__i
        """self.__i += 1
        test = True
        step = int(self.__speed)
        if step == 0 : step = 1
        if self.__position > position : step = -step
        for j in range(self.__position, position, step):
            if self.__action[i] :
                #print(time.time())
                position_deg = self.__proportionel(j)
                test = self.__arduino.controle_moteur(self.__pin, position_deg, no_sleep=True)
                temp = self.__position
                self.__position = j
                #time.sleep(self.__speed/100)
                #print(test)
                if(test):
                    logging.info("Motteur "+self.name+" : mouvement a " + str(position) +"% (" + str(position_deg) + "deg)")
                else:
                    logging.warning("Motteur "+str(self.name)+" : mouvement & " + str(position) +"% Impossible")
                    self.__position = temp
                    break
            else:
                break"""
        if self.__position != position :
            position_deg = self.__proportionel(position)
            test = self.__arduino.controle_moteur(self.__pin, position_deg, no_sleep=True)
            self.__position = position

    def stop(self):
        for i in range(0, self.__i):
            self.__action[i] = False
    
    def getPin(self)->int:
        return(self.__pin)
    
    def getCarte(self)->int:
        return(self.__arduino.getNum())
    
    def getPosition(self)->int:
        return(self.__position)
    
    def getLimit(self)->int:
        return(self.__min, self.__max)

class Head():
    __cfg : json
    __Carte : Carte
    Rotation : Moteur
    UpDown : Moteur
    Mouth : Moteur
    EyeX : Moteur
    EyeY : Moteur
    def __init__(self, cfg, carte) -> None:
        self.__cfg = cfg
        self.__Carte = carte

        self.Rotation = Moteur(self.__cfg['head']['rotation']['min'],self.__cfg['head']['rotation']['max'], self.__cfg['head']['rotation']['pin'], self.__Carte[self.__cfg['head']['rotation']['arduino']], self.__cfg['head']['rotation']['speed'] , nom="head rotation")
        self.UpDown = Moteur(self.__cfg['head']['UpDown']['min'],self.__cfg['head']['UpDown']['max'], self.__cfg['head']['UpDown']['pin'], self.__Carte[self.__cfg['head']['UpDown']['arduino']], self.__cfg['head']['UpDown']['speed'], nom="head UpDown")
        self.Mouth = Moteur(self.__cfg['head']['Mouth']['min'],self.__cfg['head']['Mouth']['max'], self.__cfg['head']['Mouth']['pin'], self.__Carte[self.__cfg['head']['Mouth']['arduino']], self.__cfg['head']['Mouth']['speed'], nom="head Mouth")
        self.EyeX = Moteur(self.__cfg['head']['EyeX']['min'],self.__cfg['head']['EyeX']['max'], self.__cfg['head']['EyeX']['pin'], self.__Carte[self.__cfg['head']['EyeX']['arduino']],self.__cfg['head']['EyeX']['speed'] , nom="head Eye X")
        self.EyeY = Moteur(self.__cfg['head']['EyeY']['min'],self.__cfg['head']['EyeY']['max'], self.__cfg['head']['EyeY']['pin'], self.__Carte[self.__cfg['head']['EyeY']['arduino']],self.__cfg['head']['EyeY']['speed'] , nom="head Eye Y")

        #self.home()
        
    def home(self):
        self.Rotation.move(self.__cfg['head']['rotation']['home']*100/(self.__cfg['head']['rotation']['max']-self.__cfg['head']['rotation']['min']))
        self.UpDown.move(self.__cfg['head']['UpDown']['home']*100/(self.__cfg['head']['UpDown']['max']-self.__cfg['head']['UpDown']['min']))
        self.Mouth.move(self.__cfg['head']['Mouth']['home']*100/(self.__cfg['head']['Mouth']['max']-self.__cfg['head']['Mouth']['min']))
        self.EyeX.move(self.__cfg['head']['EyeX']['home']*100/(self.__cfg['head']['EyeX']['max']-self.__cfg['head']['EyeX']['min']))
        self.EyeY.move(self.__cfg['head']['EyeY']['home']*100/(self.__cfg['head']['EyeY']['max']-self.__cfg['head']['EyeY']['min']))
    
    def speek(self):
        while True:
            temp = False
            time.sleep(0.1)
            try : 
                onspeek = np.load("var/onspeek.npy", allow_pickle=True)
            except:
                onspeek = False
            while onspeek:
                time.sleep(random.randint(10,100)/400)
                self.Mouth.move(random.randint(40,80))
                time.sleep(random.randint(10,100)/400)
                self.Mouth.move(random.randint(0,40))
                temp = True
                try : 
                    onspeek = np.load("var/onspeek.npy", allow_pickle=True)
                except:
                    onspeek = False
            if temp: self.Mouth.move(0)

class Right_arm():
    __cfg : json
    __Carte : Carte
    epaule_x : Moteur
    epaule_y : Moteur
    epaule_z : Moteur
    coide : Moteur
    def __init__(self, cfg, carte) -> None:
        self.__cfg = cfg
        self.__Carte = carte

        self.epaulex = Moteur(self.__cfg['right_arm']['epaule_x']['min'],self.__cfg['right_arm']['epaule_x']['max'], self.__cfg['right_arm']['epaule_x']['pin'], self.__Carte[self.__cfg['right_arm']['epaule_x']['arduino']], self.__cfg['right_arm']['epaule_x']['speed'] , nom="epaule_x")
        self.epauley = Moteur(self.__cfg['right_arm']['epaule_y']['min'],self.__cfg['right_arm']['epaule_y']['max'], self.__cfg['right_arm']['epaule_y']['pin'], self.__Carte[self.__cfg['right_arm']['epaule_y']['arduino']], self.__cfg['right_arm']['epaule_y']['speed'], nom="epaule_y")
        self.epaulez = Moteur(self.__cfg['right_arm']['epaule_z']['min'],self.__cfg['right_arm']['epaule_z']['max'], self.__cfg['right_arm']['epaule_z']['pin'], self.__Carte[self.__cfg['right_arm']['epaule_z']['arduino']], self.__cfg['right_arm']['epaule_z']['speed'], nom="epaule_z")
        self.coude = Moteur(self.__cfg['right_arm']['coude']['min'],self.__cfg['right_arm']['coude']['max'], self.__cfg['right_arm']['coude']['pin'], self.__Carte[self.__cfg['right_arm']['coude']['arduino']],self.__cfg['right_arm']['coude']['speed'] , nom="coude")

        #self.home()
        
    def home(self):
        self.epaulex.move(self.__cfg['right_arm']['epaule_x']['home']*100/(self.__cfg['right_arm']['epaule_x']['max']-self.__cfg['right_arm']['epaule_x']['min']))
        self.epauley.move(self.__cfg['right_arm']['epaule_y']['home']*100/(self.__cfg['right_arm']['epaule_y']['max']-self.__cfg['right_arm']['epaule_y']['min']))
        self.epaulez.move(self.__cfg['right_arm']['epaule_z']['home']*100/(self.__cfg['right_arm']['epaule_z']['max']-self.__cfg['right_arm']['epaule_z']['min']))
        self.coude.move(self.__cfg['right_arm']['coude']['home']*100/(self.__cfg['right_arm']['coude']['max']-self.__cfg['right_arm']['coude']['min']))
            
    
class Robot():
    __cfg : json
    __carte : Carte
    __nom : str
    __age : int
    __maker : str
    carte0 : Carte
    carte1 : Carte
    head : Head
    right_arm : Right_arm
    def __init__(self, config_path = 'config.json', log = False) -> None:
        # Config
        with open(config_path) as json_data:
            self.__cfg = json.load(json_data)
        self.__cfg = json.dumps(self.__cfg)
        self.__cfg = json.loads(self.__cfg)

        #info usuel
        self.__nom = self.__cfg['nom']
        self.__age = int(self.__cfg['age'])
        self.__maker = self.__cfg['maker']

        #controle Carte
        self.__carte = [
            Carte(self.__cfg['carte_0']['com'], self.__cfg['carte_0']['speed'], self.__cfg['carte_0']['timeout'], 0),
            Carte(self.__cfg['carte_1']['com'], self.__cfg['carte_1']['speed'], self.__cfg['carte_1']['timeout'], 1)
            ]
        self.carte0 = self.__carte[0]
        self.carte1 = self.__carte[1]
        
        #Corp
        self.head = Head(self.__cfg,self.__carte)
        self.right_arm = Right_arm(self.__cfg,self.__carte)

        #Log
        logging.info("Creation du robot " + str(self.__nom))

    def getName(self)->str:
        return(str(self.__nom))
    
    def getAge(self)->int:
        return(int(self.__age))
    
    def getMaker(self)->str:
        return(str(self.__maker))
    
    def getCarte(self)->Carte:
        return([self.carte0, self.carte1])

