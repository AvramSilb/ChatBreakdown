import time
from numpy import random
from functions import *
import threading


while True:
    txt = ReadFile("comms_args_list.txt")
    if txt != "normal":        
        args_list = txt
        t = threading.Thread(group=None, target=GetWebData, args=(args_list,))
        t.start()
        print("MAIN JUST STARTED THREAD, ", args_list)
        WriteFile("comms_args_list.txt", "normal")
    sleep(0.1)