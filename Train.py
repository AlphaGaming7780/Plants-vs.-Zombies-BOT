import torch
from ultralytics import YOLO
import os
print("Starting training ...")
print("Seting up the environement ...")
PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(PATH)

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

print("Loading model ...")
model = YOLO('plants_vs. zombies.pt')


print("Start Training...")
# Train the model
if __name__ == '__main__':
    model.train(data=PATH+"\datasets\Plants vs. Zombies V2\Plants vs. Zombies.yaml", epochs=50, imgsz=640, name = "plants-vs-zombies", device=0, batch=4, cache=False, exist_ok = True)
    model("test.png", show=True)
    os.system("pause")
    # model.export('Plants vs. Zombies TRAINED.pt')