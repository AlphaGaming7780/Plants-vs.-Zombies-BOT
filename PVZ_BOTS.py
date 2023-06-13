import pygetwindow
import pyautogui
import os
import torch
from ultralytics import YOLO
import psutil
import time
import keyboard
import json

PVZ_WINDOW_NAME = "Plants vs. Zombies" 
SCREEN_SIZE = [640, 480] # the x,y for the screen resize
GARDEN_ROW_HEIGHT = 114
GARDEN_COL_WIDTH = 85
deviceUsed = 'GPU' # OR CPU OR a specifique peripherique : 0, 1, ...
sun = 50 # The sun you have at start

# Script global variable
gardenSize = [[0,0],[0,0],[9,6]]
GardenHeightOffset = 0
plantInTheGarden = [[ "" for i in range(9)] for j in range(gardenSize[2][1])]
ZombieInTheGarden = [[ [""] for i in range(10)] for j in range(gardenSize[2][1])]
old_sun_cord_arrays = []
temp_old_sun_cord_arrays = []
Plants_Array = ["Peashooter", "Sunflower", "Cherry"]
Zombies_Array = ["Zombie", "Flag Zombie"]
gameState = "Main Menu"

print("Starting predict ...")

print("Seting up the environement ...")

PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(PATH)

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
model = YOLO('plants_vs. zombies v6.pt')
game_process = None

from roboflow import Roboflow

# rf = Roboflow(api_key="MhuazkpF1CMB9XWCQ34X")
# project = rf.workspace().project("plants-vs-zombies")
# project.version(5).deploy(model_type="yolov8", model_path=PATH+'/clc')

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
        return model.predict(source=screen, stream=False, conf=0.4, iou=0.3, save= False, show=True, device=deviceUsed, imgsz=640, exist_ok = True, verbose=False)
    except:
        # print("ERROR : ")
        time.sleep(0.5)

def ResetGame():
    global sun, old_sun_cord_arrays, temp_old_sun_cord_arrays, plantInTheGarden, ZombieInTheGarden
    sun = 50
    old_sun_cord_arrays = []
    temp_old_sun_cord_arrays = []
    plantInTheGarden = [[ "" for i in range(9)] for j in range(gardenSize[2][1])]
    ZombieInTheGarden = [[ [""] for i in range(10)] for j in range(gardenSize[2][1])]

def ClickOnSun(box_x, box_y):
    global sun, temp_old_sun_cord_arrays, old_sun_cord_arrays
    find = False
    for i in range(len(old_sun_cord_arrays)):
        old_sun_x = old_sun_cord_arrays[i][0]
        old_sun_y = old_sun_cord_arrays[i][1]
        if(old_sun_x < box_x + 5 and old_sun_x > box_x -5 and old_sun_y < box_y -5 ):
            del old_sun_cord_arrays[i]
            pyautogui.click(box_x, box_y)
            sun += 25
            print("Click on Sun the new sun amount is :", sun)
            find = True
            break

    if( not find):
        temp_old_sun_cord_arrays.append([box_x, box_y])
    return

def ClickOnReward(box_x, box_y):
    pyautogui.click(box_x, box_y)
    return

def UpdateGardenSize( box_top_left_x, box_top_left_y, box_x, box_y, box_width, box_height):
    global gardenSize, GardenHeightOffset
    gardenSize[0] = [box_top_left_x, box_top_left_y]
    gardenSize[1] = [box_x, box_y]
    gardenSize[2][1] = round(box_height/GARDEN_ROW_HEIGHT)
    GardenHeightOffset = box_y - (gardenSize[2][1]/2)*GARDEN_ROW_HEIGHT
    # print(gardenSize)
    return

def UpdatePlantsPosition(box_name, box_top_left_x, box_top_left_y):
    plant_row, plant_colum = GetCordOnTheGarden(box_top_left_x, box_top_left_y)
    if(plant_colum >= gardenSize[2][0] or plant_row >= gardenSize[2][1]):
        print('ERROR : Plant out of the garden bound \n\tPlant : ' + box_name + '\n\t [Row,Colum] : '+str(plant_row), str(plant_colum) + '\n\tGarden Size : ' + str(gardenSize[2]))
        return
    if(plantInTheGarden[plant_row][plant_colum] != box_name):
        
        plantInTheGarden[plant_row][plant_colum] = box_name
        # print("")
        # for row in plantInTheGarden:   
        #     print(row)
    return

def ZombieAreComing(box_name, box_top_left_x, box_top_left_y):

    Zombie_Row, Zombie_colum = GetCordOnTheGarden(box_top_left_x, box_top_left_y)
    # print(Zombie_Row, Zombie_colum)
    ZombieInTheGarden[Zombie_Row][Zombie_colum].append(box_name)
    # print("")
    # for row in ZombieInTheGarden:   
    #     print(row)
    return

def GetCordOnTheGarden(box_top_left_x, box_top_left_y):
    gardenTopLeftX, gardenTopLeftY = gardenSize[0]
    CordOnGarden = [box_top_left_x-gardenTopLeftX, box_top_left_y-gardenTopLeftY]
    row = int(round(CordOnGarden[1]/GARDEN_ROW_HEIGHT))
    colum = int(round(CordOnGarden[0]/GARDEN_COL_WIDTH))
    return [row, colum]

def GetGameState(results):
    global gameState
    MenuButtonIsOnScreen = False
    SeedPanelIsOnScreen = False
    PlayerHouseNameIsOnScreen = False
    PauseMenuIsOnScreen = False
    StopmenuIsOnScreen = False
    ContinueGamePanelIsOnScreen = False

    for box in results[0].boxes:
        box_name = model.names[int(box.cls)]
        if(box_name == "House Name"):
            PlayerHouseNameIsOnScreen = True
        elif(box_name == "Menu Button"):
            MenuButtonIsOnScreen = True
        elif box_name == "Seed Panel":
            SeedPanelIsOnScreen = True
        elif box_name == "Stop Menu":
            StopmenuIsOnScreen = True
        elif box_name == "Pause Menu":
            PauseMenuIsOnScreen =  True
    if(PlayerHouseNameIsOnScreen):
        gameState = "PreGame"
    elif(PauseMenuIsOnScreen or StopmenuIsOnScreen or ContinueGamePanelIsOnScreen):
        gameState = "Pause"
    elif(MenuButtonIsOnScreen and SeedPanelIsOnScreen):
        gameState = "Playing"

def main() :
    global old_sun_cord_arrays, temp_old_sun_cord_arrays, plantInTheGarden, ZombieInTheGarden, gameState
    while(psutil.pid_exists(game_process)):

        plantInTheGarden = [[0 for i in range(9)] for j in range(gardenSize[2][1])]
        ZombieInTheGarden = [[ [""] for i in range(10)] for j in range(gardenSize[2][1])]
        if(keyboard.is_pressed("q")) : 
            quit()

        results = GetFrameResults()

        if(results == None):
            continue

        GetGameState(results)
        # print(results)
    
        left, top = game.topleft
        temp_old_sun_cord_arrays = []
        for box in results[0].boxes:
            box_x, box_y, box_width, box_height = [(box.xywh[0][0]).item()+left+4, box.xywh[0][1].item()+top+40, box.xywh[0][2].item(), box.xywh[0][3].item()]
            box_top_left_x, box_top_left_y, box_bottom_right_x, box_bottom_right_x = [(box.xyxy[0][0]).item()+left+4, box.xyxy[0][1].item()+top+40, box.xyxy[0][2].item(), box.xyxy[0][3].item()]
            box_name = model.names[int(box.cls)]
            if(box_name == "Sun" and gameState == 'Playing') :
                ClickOnSun(box_x, box_y)
            elif(box_name  == "Reward" and gameState == 'Playing'):
                ClickOnReward(box_x, box_y)
            elif(box_name == "Garden" and gameState == 'Playing'):
                UpdateGardenSize(box_top_left_x, box_top_left_y, box_x, box_y, box_width, box_height)
            elif(Plants_Array.count(box_name) > 0 and gameState == 'Playing'):
                UpdatePlantsPosition(box_name, box_top_left_x, box_top_left_y)
            elif(Zombies_Array.count(box_name) > 0 and gameState == 'Playing'):
                ZombieAreComing(box_name, box_x, box_y)
        


        old_sun_cord_arrays = temp_old_sun_cord_arrays

main()