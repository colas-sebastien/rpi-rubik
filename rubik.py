import sys
sys.path.insert(1, '/home/pi/lcd')
import drivers
import time
from curio import sleep
from bricknil import attach, start
from bricknil.hub import PoweredUpHub
from bricknil.sensor import WedoMotor
from bricknil.sensor import ExternalMotor
import logging, sys
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import subprocess
import kociemba
import numpy as np
import math

VERSION = "Rubik Solver 1.3"

@attach(ExternalMotor, name='retourne',port=0, capabilities=['sense_speed'])
@attach(ExternalMotor, name='rotation',port=1, capabilities=['sense_speed'])
class Rubik(PoweredUpHub):
    angle_ajustemment=300
    angle_rotation=450
    angle_ajuste=70
    angle_ajuste_droite=70
    angle_ajuste_2=70
    vitesse_rotation=100

    angle_debut=0
    angle_debloque=1000
    angle_fin_retourne=2200
    angle_bloque=3400
    angle_retourne=5700

    vitesse_retourne=100

    retourne_vitesse=0
    rotation_vitesse=0

    table_conversion = {
        "B":    "b1B",
        "B'":   "b4B",
        "B2":   "b2B",
        "D":    "cCb1cCcCcC",
        "D'":   "cCb4cCcCcC",
        "D2":   "cCb2cCcCcC",
        "F":    "cCcCb1cCcC",
        "F'":   "cCcCb4cCcC",
        "F2":   "cCcCb2cCcC",
        "R":    "B3cCb1cCcCcCB0",
        "R'":   "B3cCb4cCcCcCB0",
        "R2":   "B3cCb2cCcCcCB0",
        "L":    "B0cCb1cCcCcCB3",
        "L'":   "B0cCb4cCcCcCB3",
        "L2":   "B0cCb2cCcCcCB3",
        "U":    "cCcCcCb1cC",
        "U'":   "cCcCcCb4cC",
        "U2":   "cCcCcCb2cC"
    }

############################################################
# Fonctions d'étalonnage de la rotation
############################################################

    def correction_rotation(self):
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array

        edges = cv2.Canny(image,50,150,apertureSize = 3)
        minLineLength=200
        lines = cv2.HoughLinesP(image=edges,rho=1,theta=np.pi/180, threshold=100,lines=np.array([]), minLineLength=minLineLength,maxLineGap=80)

        a,b,c = lines.shape
        angles = []
        for i in range(a):
            if ((lines[i][0][2]-lines[i][0][0])!=0):
                angle=round(math.atan((lines[i][0][3]-lines[i][0][1])/(lines[i][0][2]-lines[i][0][0])),2)
                if (math.fabs(angle) < math.pi/4):
                    cv2.line(image, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 3, cv2.LINE_AA)
                    angles.append(angle)
                cv2.imwrite('images/etalonnage.jpg',image)

        dict = {}
        for angle in angles:
            if (angle in dict.keys()):
                dict[angle] = dict[angle] + 1
            else:
                dict[angle] = 1

        max_number = 0
        max_angle = 0
        for angle in dict.keys():
            if dict[angle] > max_number :
                max_angle=angle
                max_number=dict[angle]

        return max_angle

    async def etalonne_rotation(self,precision):    
        display.lcd_display_string("Etalonnage      ", 2)
        for i in range(precision):
            angle=int(self.correction_rotation()*self.angle_ajustemment)
            if (angle < 0):
                await self.rotation.rotate(angle, speed=-self.vitesse_rotation)
            else:
                await self.rotation.rotate(angle, speed=self.vitesse_rotation)
            await self.attente_rotation() 


############################################################
# Fonctions pour attendre la fin d'un mouvement
############################################################
    async def retourne_change(self):
        speed = self.retourne.value[ExternalMotor.capability.sense_speed]
        self.retourne_vitesse=speed

    async def rotation_change(self):
        speed = self.rotation.value[ExternalMotor.capability.sense_speed]
        self.rotation_vitesse=speed

    async def attente_retourne(self):
        await sleep(0.5)
        while (self.retourne_vitesse != 0) :
            await sleep(0.1)

    async def attente_rotation(self):
        await sleep(0.5)
        while (self.rotation_vitesse != 0) :
            await sleep(0.1)

############################################################
# Pour tourner le Rubik's cube (rotation)
############################################################
    async def tourne_gauche(self):                          # 0
        await self.rotation.rotate(self.angle_rotation, speed=self.vitesse_rotation)
        await self.attente_rotation()

    async def tourne_gauche_2(self):                        # 5
        await self.rotation.rotate(self.angle_rotation*2, speed=self.vitesse_rotation)
        await self.attente_rotation()

    async def manipule_gauche(self):                        # 1
        await self.rotation.rotate(self.angle_rotation+self.angle_ajuste, speed=self.vitesse_rotation)
        await self.attente_rotation()
        await self.rotation.rotate(self.angle_ajuste, speed=-self.vitesse_rotation)
        await self.attente_rotation()

    async def manipule_gauche_2(self):                      # 2
        await self.rotation.rotate(self.angle_rotation*2+self.angle_ajuste_2, speed=self.vitesse_rotation)
        await self.attente_rotation()
        await self.rotation.rotate(self.angle_ajuste_2, speed=-self.vitesse_rotation)
        await self.attente_rotation()

    async def tourne_droite(self):                          # 3
        await self.rotation.rotate(self.angle_rotation, speed=-self.vitesse_rotation)
        await self.attente_rotation()

    async def manipule_droite(self):                        # 4
        await self.rotation.rotate(self.angle_rotation+self.angle_ajuste_droite, speed=-self.vitesse_rotation)
        await self.attente_rotation()
        await self.rotation.rotate(self.angle_ajuste_droite, speed=self.vitesse_rotation)
        await self.attente_rotation()

############################################################
# Pour bouger le bras de manipulation du Rubik's Cube
############################################################
    async def position_param(self,pos):
        await self.retourne.set_pos(pos, speed=self.vitesse_retourne)
        await self.attente_retourne()

    async def position_debut(self):                         # a
        await self.position_param(self.angle_debut)

    async def position_bloque(self):
        await self.position_param(self.angle_bloque)        # b

    async def position_debloque(self):                      # B
        await self.position_param(self.angle_debloque)

    async def position_retourne(self):                      # c
        await self.position_param(self.angle_retourne)

    async def position_fin_retourne(self):                  # C
        await self.position_param(self.angle_fin_retourne)

    async def retourne_rubik(self):
        await self.position_retourne()                  
        await self.position_debloque()
            

############################################################
# Mouvements Rubik's Cube
############################################################

    async def lecture_cube(self):
        # FACE 1 (devant)
        display.lcd_display_string("Photo 1/6      F", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        cv2.imwrite('images/rubiks-side-F.png',image)

        await self.retourne_rubik()

        # FACE 2 (dessus)
        display.lcd_display_string("Photo 2/6      U", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        cv2.imwrite('images/rubiks-side-U.png',image)

        await self.tourne_gauche()
        await self.retourne_rubik()

        # FACE 3 (droite)
        display.lcd_display_string("Photo 3/6      R", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        M = cv2.getRotationMatrix2D((320,240),180,1.0)
        image=cv2.warpAffine(image,M,(640,480))
        cv2.imwrite('images/rubiks-side-R.png',image)

        await self.tourne_droite()
        await self.retourne_rubik()

        # FACE 4 (derriere)
        display.lcd_display_string("Photo 4/6      B", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        M = cv2.getRotationMatrix2D((320,240),270,1.0)
        image=cv2.warpAffine(image,M,(640,480))
        cv2.imwrite('images/rubiks-side-B.png',image)

        await self.tourne_gauche()
        await self.retourne_rubik()

        # FACE 5 (dessous)
        display.lcd_display_string("Photo 5/6      D", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        cv2.imwrite('images/rubiks-side-D.png',image)

        await self.tourne_droite()
        await self.retourne_rubik()

        # FACE 6 (gauche)
        display.lcd_display_string("Photo 6/6      L", 2) 
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format='bgr')
        image=rawCapture.array
        cv2.imwrite('images/rubiks-side-L.png',image)

        await self.tourne_gauche()
        await self.retourne_rubik()
        await self.tourne_droite()
        await self.position_debut()

        return

    async def decode_cube(self):
        display.lcd_display_string("Decodage du cube", 2) 

        try:    
            decodage = (
                subprocess.check_output(
                    ["rubiks-cube-tracker.py", "--directory", "images"]
                )
                .decode("ascii")
                .splitlines()[0]
                .strip()
            )
        except subprocess.CalledProcessError as e:
            display.lcd_display_string("Erreur lecture  ", 2)
            exit            
        f = open("tracker.json","w")
        f.write(decodage)
        f.close()
        display.lcd_display_string("Fin decodage    ", 2) 
        return

    async def resolution_cube(self):
        display.lcd_display_string("Resolution  cube", 2) 

        try:    
            self.cube = (
                subprocess.check_output(
                    ["rubiks-color-resolver.py", "--filename", "tracker.json"]
                )
                .decode("ascii")
                .splitlines()[0]
                .strip()
            )
        except subprocess.CalledProcessError as e:
            display.lcd_display_string("Erreur resolutio", 2)
            exit            
        self.mouvements=kociemba.solve(self.cube)
        return
    
    async def run(self):
        display.lcd_display_string("                ", 2) # Write line of text to second line of display

        await self.etalonne_rotation(1)
        await self.lecture_cube()
        await self.decode_cube()
        await self.resolution_cube()        

        print("cube:")
        print(self.cube)
        print("resolution:")
        print(self.mouvements)        

        self.mouvements_simples=""

        if (True):
            for mouvement in self.mouvements.split():  
                self.mouvements_simples+=self.table_conversion[mouvement];             
            print("mouvements:")
            print(self.mouvements_simples)
            
            ##### Réduction du nombre de mouvements ###################################

            # On retourne 4 fois
            self.mouvements_simples=self.mouvements_simples.replace('cCcCcCcC','')

            # Au début le bras est déjà levé
            if (self.mouvements_simples.startswith('B')):
                self.mouvements_simples=self.mouvements_simples[1:]

            # Retourner 3 fois => tourner, retourner, tourner
            self.mouvements_simples=self.mouvements_simples.replace('cCcCcC','B5cB5')

            self.mouvements_simples=self.mouvements_simples.replace('B5B5','B')
            self.mouvements_simples=self.mouvements_simples.replace('B5B3','B0')
            self.mouvements_simples=self.mouvements_simples.replace('B3B5','B0')
            self.mouvements_simples=self.mouvements_simples.replace('B5B0','B3')
            self.mouvements_simples=self.mouvements_simples.replace('B0B5','B3')
            self.mouvements_simples=self.mouvements_simples.replace('Bc','c')
            self.mouvements_simples=self.mouvements_simples.replace('BB','B')            
            self.mouvements_simples=self.mouvements_simples.replace('CB','B')
            self.mouvements_simples=self.mouvements_simples.replace('3B0','')

            # On finit par retourner
            while (self.mouvements_simples.endswith('cC')):
                self.mouvements_simples=self.mouvements_simples[:-2]
            # On finit par relever le bras
            if (   self.mouvements_simples.endswith('0')
                or self.mouvements_simples.endswith('3')
                or self.mouvements_simples.endswith('5')
                or self.mouvements_simples.endswith('c')
                or self.mouvements_simples.endswith('B')):
                self.mouvements_simples=self.mouvements_simples[:-1]

            ###########################################################################
            print("mouvements (après optimisation):")
            print(self.mouvements_simples)
            nb=len(self.mouvements_simples)
            await self.etalonne_rotation(1)
            for mouvement in self.mouvements_simples:
                display.lcd_display_string("Mouvements: "+str(nb)+" ", 2)
                print(mouvement, end="", flush=True)
                nb-=1
                if   (mouvement == "0"):
                    await self.tourne_gauche()
                elif (mouvement == "1"):
                    await self.manipule_gauche()
                elif (mouvement == "2"):
                    await self.manipule_gauche_2()
                elif (mouvement == "3"):
                    await self.tourne_droite()
                elif (mouvement == "4"):
                    await self.manipule_droite()
                elif (mouvement == "5"):
                    await self.tourne_gauche_2()
                elif (mouvement == "a"):
                    await self.position_debut()
                elif (mouvement == "b"):
                    await self.position_bloque()
                elif (mouvement == "B"):
                    await self.position_debloque()
                elif (mouvement == "c"):
                    await self.position_retourne()
                elif (mouvement == "C"):
                    await self.position_fin_retourne()
                else:
                    pass

        print("\n")
        await self.position_debut()
        display.lcd_display_string("Fin             ", 2)

async def system1():
    rotation = Rubik('Rubik')

if __name__ == '__main__':
    display = drivers.Lcd()
    display.lcd_display_string(VERSION, 1) # Write line of text to first line of display
    display.lcd_display_string("                ", 2) # Write line of text to second line of display
    camera = PiCamera()
    camera.resolution=(640,480)
    camera.rotation=180
    #logging.basicConfig(level=logging.DEBUG)
    display.lcd_display_string("Connexion Lego..", 2) # Write line of text to second line of display
    start(system1)

