import os
import torch
from ultralytics import YOLO

print("Starting predict ...")
print("Seting up the environement ...")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

deviceUsed = 'GPU' # OR CPU OR a specifique peripherique : 0, 1, ...

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
    deviceUsed = 'cpu'

print("Loading Model ...")
model = YOLO('plants_vs. zombies v2.pt')

print("Start Predict...")
# visualize your prediction
model.predict("in.mp4", conf=0.4, iou=0.3, save= False, show=True, device=deviceUsed)

os.system('pause')
