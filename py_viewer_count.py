from copy import copy
from time import sleep
from functions import *
import copy

constants_2 = ReadFile("constants.txt")

WriteFile("comms_args_list.txt", "normal")

def StartSave(channel, comms_info):
    print("start of saving", channel)

    f_n = comms_info[0]
    date_time = comms_info[1]


    print("BEFORE start of thread")

    args_list = [f_n, channel, date_time]

    # process = Process(target=GetWebData, args=(args_list,))
    # process.start()
    WriteFile("comms_args_list.txt", args_list)

    while True:
        try:
            while ReadFile("comms_args_list.txt") != "normal":
                print("VC waiting for thread to start")
                sleep(0.5)
            break
        except:
            print("ERR IN READING FILE COMMS ARGS LIST")
            sleep(0.5)

    
    while True:
        try:
            r = ReadFile("comms_args_list.txt")
            if r != "normal":
                print("VC waiting for thread to start")
                sleep(0.5)
            else:
                break
        except:
            sleep(0.2)

    print("VC Back to normal")
    
def WaitConfirmDataSaved():
    comms = ReadFile("comms_need_save_view_count.txt")
    while comms[0] == "sent to js":
        print("waiting for app static to save")
        sleep(0.4)
        comms = ReadFile("comms_need_save_view_count.txt")
    if comms[0] == "Failed save requirement":
        return "Failed save requirement"
    return comms[1]

WriteFile("comms_need_save_view_count.txt", ["normal", []])

view_count_info = {}
processes = []

live_info = {channel : False for channel in constants_2["channels"] }
prev_live_info = {channel : False for channel in constants_2["channels"] }
need_save_d = {channel : False for channel in constants_2["channels"] }
saving_bool = False


TCT_max =  12 # 15 * 12 = 3mins
TCT_counter = 0
need_to_reset = False

while True:
    #print(TCT_counter)
    #print("in main loop")

    for channel in constants_2["channels"]:

        
        if TCT_counter % TCT_max == 0:
            is_live = SaveTTVC(channel, True)
            need_to_reset = True
        else:
            is_live = SaveTTVC(channel, False)

        
        live_info[channel] = is_live

            
        #print(channel, live_info[channel], prev_live_info[channel])
        if prev_live_info[channel] and not live_info[channel]:
            saving_bool = True
            need_save_d[channel] = True
        if not prev_live_info[channel] and live_info[channel]:
            print("STREAM JUST STARTED", channel)
            #ResetTTVC(channel)

                
    if saving_bool:
        WriteFile("comms_need_save_view_count.txt", ["sent to js", need_save_d])
        comms_info = WaitConfirmDataSaved()
        if comms_info == "Failed save requirement":
            print("Failed save requirement")
        else:
            for channel in constants_2["channels"]:
                if need_save_d[channel]:
                    StartSave(channel, comms_info[channel])
                    need_save_d[channel] = False
        
        saving_bool = False
        WriteFile("comms_need_save_view_count.txt", ["normal", []])


    #print("end of loop")
    TCT_counter += 1

    printing_live_info = []
    for channel in live_info.keys():
        if live_info[channel]:
            printing_live_info.append(channel)
    print("live: ", printing_live_info)
    
    prev_live_info = copy.deepcopy(live_info)

    
    if need_to_reset:
        print("3min mark")
        TCT_counter = 1
        need_to_reset = False
    sleep(constants_2["update_time"])
    
    

    