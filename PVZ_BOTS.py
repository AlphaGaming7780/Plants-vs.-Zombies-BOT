import cv2
import numpy as np
import pygetwindow
import pyautogui
import os
import torch
from ultralytics import YOLO
import psutil
import time
import keyboard
from ultralytics.yolo.utils.plotting import Annotator

PVZ_WINDOW_NAME = "Plants vs. Zombies" 
SCREEN_SIZE = [640, 480] # the x,y for the screen resize
deviceUsed = 'GPU' # OR CPU OR a specifique peripherique : 0, 1, ...
sun = 50 # The sun you jave at start
print("Starting predict ...")

print("Seting up the environement ...")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if (torch.cuda.is_available()) :
    print("Cuda Avaible")
    print("Device count : " + str(torch.cuda.device_count()))
    for i in range(torch.cuda.device_count()):
        print("\t"+str(i)+" : "+str(torch.cuda.get_device_name(i)))

    if deviceUsed.lower() == 'gpu':
        deviceUsed = torch.cuda.current_device()
        print("Current device : " + str(deviceUsed) + " ("+str(torch.cuda.get_device_name(deviceUsed))+")")
    elif deviceUsed.lower() != 'cpu':
        print("Current device : " + str(deviceUsed) + " ("+str(torch.cuda.get_device_name(deviceUsed))+")")
    else:
        print("Current device : " + str(deviceUsed))
else : 
    print("Cuda isn't Avaible")

print("Loading Model ...")
model = YOLO('plants_vs. zombies v2.pt')
game_process = None

while game_process == None :
    print("Sherching the game...")
    for proc in psutil.process_iter():
        if 'PlantsVsZombies.exe' in proc.name():
            game_process = proc.pid
            break

game = pygetwindow.getWindowsWithTitle(PVZ_WINDOW_NAME)[0]


def GetFrameResults() : 
    try:
        game.activate()
        left, top = game.topleft
        screen = pyautogui.screenshot(region=(left+4, top+40, game.width-8, game.height-42))
        # screen = screen.resize(size=[640,480])
        return model.predict(source=screen, conf=0.4, iou=0.3, save= False, show=True, device=deviceUsed, imgsz=640, exist_ok = True)
    except:
        # print("ERROR : ")
        time.sleep(0.5)


def main() :
    while(psutil.pid_exists(game_process)):

        if(keyboard.is_pressed("q")) : 
            quit()
        
        results = GetFrameResults()
        # print(results)
    
        left, top = game.topleft
        for box in results[0].boxes:
            box_x, box_y, box_width, box_height = [(box.xywh[0][0])+left+4, box.xywh[0][1]+top+40, box.xywh[0][2], box.xywh[0][3]]  # *width/640 *height/480
            # print(box_cord)
            box_name = model.names[int(box.cls)]
            if(box_name == "Sun") :
                # print(pyautogui.position())
                # print(box_x, box_y)
                pyautogui.click(box_x, box_y)


main()
