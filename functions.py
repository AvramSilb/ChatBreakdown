
from difflib import SequenceMatcher
import math
import os
from time import sleep, time, strptime, localtime, strftime
import requests
import json
from datetime import date, datetime, timedelta
from itertools import zip_longest
import csv
import smtplib, ssl
from functions import *
from collections import Counter
import pathlib
from calendar import timegm
import shutil
import boto3


def WriteFile(file_name, data):
    
    with open(file_name, 'w') as f:
        json.dump(data, f) 
        f.close()


def ReadFile(file_name):

    file = open(file_name, encoding='utf-8')
    file_1 = file.read()
    file_2 = json.loads(file_1)
    file.close()
    return file_2

constants_2 = ReadFile("constants.txt")

def MakeFolder(extra_path, new_folder_name):
    curr_p = str(pathlib.Path().resolve())
    print("extra p", curr_p + extra_path)
    f_path  = curr_p + extra_path + "./"  + new_folder_name
    print("f_path", f_path)
    os.mkdir(f_path)

def GetTitleCategory(channel):
    
    
    channel_id_str = str(getUserID(channel))

    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/channels?broadcaster_id=" + channel_id_str)
    #print(jsoninfo)
    title = jsoninfo["data"][0]["title"]
    category = jsoninfo["data"][0]["game_name"]
    return title, category


def GetEmotePercentage(msg_slot):
    
    count = 0
    for msg in msg_slot:
        if msg["emote_info"] != None:
            count += 1
    return round((count/len(msg_slot)) * 100, 2)



def SaveCurrThumbnail(channel, url_raw):
    

    url_1 = url_raw
    w = 2 * 192
    h = 2 * 108
    url_2 = url_1.replace("{width}", str(w))
    url = url_2.replace("{height}", str(h))

    

    page = requests.get(url)
    f_ext = os.path.splitext(url)[-1]
    f_name = GetTimeDateStr()  + f_ext        
    total_path = "./Thumbnails/"  + channel + "/"  + str(int(time())) + "__" +  f_name 
    try:
        with open(total_path, 'wb') as f:
            f.write(page.content)        
    except:
        print("except")
        MakeFolder("./Thumbnails/", channel)
        SaveCurrThumbnail(channel, url_raw)






def GetMainTitleAndCategoryDict(stream_start_time, stream_end_time, title_category_dict):


    if title_category_dict == {}:
        print("NO CAT TITLE INFO")
        return None

    print("start t", stream_start_time)
    print("end t", stream_end_time)
    #print(title_category_dict)

    t_c_times =  list(title_category_dict.keys())
    t_c_times = [int(t) for t in t_c_times]
    t_i = len(t_c_times) - 1

    #print(title_category_dict)

    if t_i == 0:
        main_title = title_category_dict[str(t_c_times[0])]["title"]
        category = title_category_dict[str(t_c_times[0])]["category"]
        category_change_dict = {str(t_c_times[0]): category}
        return main_title, category_change_dict


    print("T_i 117", t_i)
    while t_i > 0 and t_c_times[t_i] > stream_end_time:
        t_i -= 1
    end_time_i = t_i
    if t_i == 0:
        print("STARRT END SAME TIME 135")
        start_time_i = 0
    else:
        while t_i > 0 and t_c_times[t_i] > stream_start_time:
            t_i -= 1
        start_time_i = t_i

    mid_i = start_time_i + int((end_time_i - start_time_i)/2)
    print(mid_i)
    main_title = title_category_dict[str(t_c_times[mid_i])]["title"]
    main_title.replace('"', "'")
    print("main title:", mid_i, str(t_c_times[mid_i]), main_title)





    category_list = [x["category"] for x in list(title_category_dict.values())]
    
    
    #category_change_dict = {str(t_c_times[0]): category_list[0]}
    category_change_dict = {str(t_c_times[start_time_i]): category_list[start_time_i]}
    
    
    #curr_cat = category_list[0]
    curr_cat = category_list[start_time_i]
    #c_i = 0
    c_i = start_time_i
    #while c_i < len(category_list):
    while c_i <= end_time_i:
        if curr_cat == category_list[c_i]:
            c_i += 1
        else:
            category_change_dict[str(t_c_times[c_i])] = category_list[c_i]
            curr_cat = category_list[c_i]
            c_i += 1
        

    #reset Titlecatregory info general
    
    #ResetTTVC(channel)

    return main_title, category_change_dict

    

def RemoveOldStreams(final_day_int):
    x = ReadFile("./web_data/web_data_file_names.txt")

    for channel in list(x.keys()):
        for p in list(x[channel].keys()):
            t = int(p[7:9])
            if t <= final_day_int:
                x[channel].pop(p)

    WriteFile("./web_data/web_data_file_names.txt", x)
    print("done")

def GetTimeoutTotalLength(t_list, timeout_dict, timeout_times_list):
    res = [0 for k in range(len(t_list))]
    
    i = 0
    j = 0
    while j < len(t_list):
        while i < len(timeout_times_list) and timeout_times_list[i] <  t_list[j]:
            res[j] += int(timeout_dict[i]["ban-duration"])
            
            i+=1
        j+= 1
    return res



def GetTimeoutListPerInterval(t_list, timeout_times_list):
    #MAKE SURE TIMES ARE SMAE FORMAT
    res = [0 for k in range(len(t_list))]
    
    i = 0
    j = 0
    while j < len(t_list):
        while i < len(timeout_times_list) and int(timeout_times_list[i]) <  t_list[j]:
            res[j] += 1
            i+=1
        j+= 1
    return res


def CountDict(dict):
    L = dict

    d = {}
    for x in L:
        if x in d:
            d[x] = d[x] + 1
        else:
            d[x] = 1

    y = sorted(d.keys(), key=lambda k: d[k], reverse=True)
    v = [d[k] for k in y ]

    return {"key_l" : y,"value_l" : v}

    



def GetWebData(args_list):
    

    #[all_data_f_n, curr_channel, view_count_info, date_time]
    all_data_f_n = args_list[0]
    curr_channel = args_list[1]
    date_time = args_list[2] 
    



    all_data_including_other = ReadFile("./all_data/" + all_data_f_n)
    
    all_data = all_data_including_other["normal_all_data"]
    timeout_info = all_data_including_other["timeout_info"]
    deleted_msgs = all_data_including_other["deleted_msgs"]
    bans = all_data_including_other["bans"]


    stream_end_time = int(all_data[-1]["time"])
    

    TTVC = ReadFile("./TTVC/" +  curr_channel + "_TTVC.txt")

    start_time_str_list = TTVC["api_start_time_str"]
    stream_start_time = GetStartTimeFromEndTime(start_time_str_list, stream_end_time)
    



    view_count_info = TTVC["VC_dict"]
    #vc_info_ordered = GetOrderedVCInfo(curr_channel, view_count_info)


    


    print("START END TIMES------")
    print("start",  stream_start_time)
    print("end", stream_end_time)
    stream_len_hour =  (stream_end_time - stream_start_time)/(1000 * 3600)
    print("stream len hour",  stream_len_hour)

    timeout_times_list = [int(x["time"]) for x in timeout_info]
    


    minimum_msgs = constants_2["minimum_msgs"]

    print("num msgs including offline", len(all_data))

    if len(all_data) < minimum_msgs:
        print("not enough msgs including offline")
        return None
    if stream_len_hour < 0.2:
        print("stream less than 12mins")
        return None
    if len(view_count_info["times"]) < 2:
        print("not enough view count info")
        return None


    time_delta_s = constants_2["time_delta_s"] 
    time_delta_ms = time_delta_s * 1000


    last_msg_time = int(all_data[-1]["time"])
 
    if last_msg_time < stream_start_time:
        print("ALL MSGS BEFORE STREAM START")
        return None
    
    print("stream start time excluding pop", stream_start_time)
    #print("all data before pop", all_data)
    


    
    msgs_removed_before_start  = 0
    while int(all_data[0]["time"]) < stream_start_time and len(all_data) > 0:
        all_data.pop(0)
        msgs_removed_before_start += 1
    msgs_removed_after_end  = 0
    while int(all_data[-1]["time"]) > stream_end_time and len(all_data) > 0:
        all_data.pop(-1)
        msgs_removed_after_end += 1
    
    print("msgs_removed_before_start", msgs_removed_before_start)
    print("msgs_removed_after_end", msgs_removed_after_end)

    #print("all data AFTER pop", all_data)
    if len(all_data) < minimum_msgs:
        print("not enough msgs excluding offline")
        return None


    first_msg_time = int(all_data[0]["time"])
    stream_length_vc_s = int((stream_end_time - stream_start_time)/1000)
    stream_length_msg_s = int((last_msg_time - first_msg_time)/1000)
    print("stream_length_vc_s", stream_length_vc_s)
    print("stream_length_msg_s", stream_length_msg_s)



    if stream_length_vc_s < 2 * time_delta_s:
        print("stream view count length not long enough")
        return None
    
    if stream_length_msg_s < 2 * time_delta_s:
        print("stream msg length not long enough")
        return None

    print("REMOVEING FALSE VC TIMES")


    VC_removed_before_start  = 0
    while len(view_count_info["times"]) > 0 and int(view_count_info["times"][0]) < stream_start_time :
        view_count_info["times"].pop(0)
        view_count_info["views"].pop(0)
        VC_removed_before_start += 1
    VC_removed_after_end  = 0
    while len(view_count_info["times"]) > 0 and int(view_count_info["times"][-1]) > stream_end_time:
        view_count_info["times"].pop(-1)
        view_count_info["views"].pop(-1)
        VC_removed_after_end += 1
    
    print("VC_removed_before_start", VC_removed_before_start)
    print("VC_removed_after_end", VC_removed_after_end)


    times_list = GetTimesList(all_data, time_delta_ms)
    #print("get web data times list: ", times_list)

    times_list_mins = GetTimeListMinutes(times_list)

    analysis_all, need_f_info_list, final_word_dict = GetAnalysisAll(all_data, curr_channel, times_list, time_delta_ms)


    #add all new following info
    chatter_follower_info = ReadFile("chatter_info.txt")
    updated_chatter_info = UpdateChatterInfo(chatter_follower_info, need_f_info_list)
    WriteFile("chatter_info.txt", updated_chatter_info)
    print("SAVED NEW CHATTER INFO")



    


    chatters_percentage_arr = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5] 
    num_msg_per_x_top_chatters_list, color_popular_list_sub_20 = GetNumMsgsPerXTopChattersAndPopularColors(all_data, chatters_percentage_arr)
    


    #NEW EMOTE
    emotes_top_all = GetTopEmoteTotall(all_data)
    emote_top_moments = GetTopEmoteMoments(analysis_all)
    

    color_list = [msg["color"] for msg in all_data]
    temp_color = CountDict(color_list)

    color_nums = temp_color["value_l"]
    color_names = temp_color["key_l"]

    while None in color_names:
        none_i = color_names.index(None)
        print("NONE COLOR", none_i)
        color_names.pop(none_i)
        color_nums.pop(none_i)

    try: 
        color_nums = color_nums[:50] 
        color_names = color_names[:50]
    except:
        print("LESS THEN 50 COLORS")






    timeout_num_web_data_list = GetTimeoutListPerInterval(times_list, timeout_times_list)
    

    timeout_total_length_web_data_list = GetTimeoutTotalLength(times_list, timeout_info, timeout_times_list)

    bans_web_data_list = GetTimeoutListPerInterval(times_list, bans)
    deleted_msgs_web_data_list = GetTimeoutListPerInterval(times_list, deleted_msgs)

    normal_data_in_order_dict = GetNormalDataInOrderDict(analysis_all, times_list)

    times_hms = GetTimeHourMinFormatList(times_list_mins)
    formatted_page_name = ConvertPageNames(date_time, stream_start_time, stream_end_time)

    stream_len_hour = (stream_end_time - stream_start_time)/(1000 * 3600)
    print("STREAM LEN HOURS", stream_len_hour)

    normal_data_in_order_dict["timeout_num"] = timeout_num_web_data_list
    normal_data_in_order_dict["timeout_length"] =timeout_total_length_web_data_list
    normal_data_in_order_dict["bans_num"] = bans_web_data_list
    normal_data_in_order_dict["deleted_msgs_num"] = deleted_msgs_web_data_list

    stream_results = GetStreamResults(normal_data_in_order_dict, stream_len_hour)
    stream_results["top_one_percent_chatters"] = num_msg_per_x_top_chatters_list[0]

    diff_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    thumbnails_info = GetNThumbnailsList(10, diff_list, curr_channel, stream_start_time, stream_end_time)
    thumbnail_axis_img_f_n = thumbnails_info["file_names"]
    thumbnail_axis_img_labels = thumbnails_info["labels"]

    for t_f_n in thumbnail_axis_img_f_n:
        shutil.copy("./Thumbnails/" + curr_channel + "/" + t_f_n, "./THUMBNAILS_USED/" + curr_channel + "/" + t_f_n)


    print("CHANNEL:", curr_channel)
    stream_title, category_change_dict = GetMainTitleAndCategoryDict(stream_start_time, stream_end_time, TTVC["TC_dict"])


    channel_display_name = GetDisplayName(curr_channel)


    web_data = {
    "times" : times_list_mins,
    "times_hms" : times_hms,
    "keys" : normal_data_in_order_dict,
    "emote_moments" : emote_top_moments,
    "emote_top_all" : emotes_top_all,
    "num_msg_per_x_top_chatters" : num_msg_per_x_top_chatters_list,
    "view_count_info" : view_count_info,
    "color_names" : color_names,
    "color_nums" : color_nums,
    "stream_results" : stream_results,
    "thumbnail_axis_img_f_n" : thumbnail_axis_img_f_n,
    "thumbnail_axis_img_labels" : thumbnail_axis_img_labels, 
    "formatted_page_name" : formatted_page_name,
    "stream_title" : stream_title,
    "category_change_dict" : category_change_dict,
    "channel_display_name" : channel_display_name,
    "channel_name" : curr_channel,
    "stream_start_time" : stream_start_time,
    "stream_end_time" : stream_end_time,
    "popular_colors_names" : color_popular_list_sub_20[0], 
    "popular_colors_num" : color_popular_list_sub_20[1]
    }



    file_name = "web_data" + date_time + curr_channel + ".txt"
    try:
        WriteFile("./web_data/" + curr_channel + "/" + file_name, web_data)
    except:
        MakeFolder("./web_data", curr_channel)
        WriteFile("./web_data/" + curr_channel + "/" + file_name, web_data)

    
    print("Saved WEB DATA", file_name)

    WriteFile("./WordCounter/" + curr_channel  + "/" + date_time + "__WordCount.txt", final_word_dict)
    print("SAVED WORDDICT")



    web_data_file_names = ReadFile("./web_data/web_data_file_names.txt")

    if curr_channel not in web_data_file_names:
        web_data_file_names[curr_channel] = {}    

    web_data_file_names[curr_channel][date_time] = {"file_name" : file_name, "stream_start_time" :stream_start_time, "stream_end_time" : stream_end_time, "formatted_page_name" : formatted_page_name, "stream_results" : stream_results, "title" : stream_title, "category_change_dict" : category_change_dict, "color_names" : color_names, "color_nums" : color_nums, "popular_colors_names" : color_popular_list_sub_20[0], "popular_colors_num" : color_popular_list_sub_20[1]}



    WriteFile("./web_data/web_data_file_names.txt", web_data_file_names)

    #S3 SYNC

    access_key = constants_2["AWS_access_key"]
    secret_access_key = constants_2["AWS_secret_access_key"]
    bucket_name = constants_2["AWS_bucket_name"]
    
    s3_res = boto3.resource(
        's3',
        region_name='us-east-1',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key
    )

    s3_res.meta.client.upload_file("./web_data/" + curr_channel + "/" + file_name, bucket_name, "InstanceSetup/web_data/" + curr_channel + "/" + file_name)

    for t_f_n in thumbnail_axis_img_f_n:
        s3_res.meta.client.upload_file("./THUMBNAILS_USED/" + curr_channel + "/" + t_f_n, bucket_name, "InstanceSetup/THUMBNAILS_USED/" + curr_channel + "/" + t_f_n)

    s3_res.meta.client.upload_file("./WordCounter/" + curr_channel  + "/" + date_time + "__WordCount.txt", bucket_name, "InstanceSetup/WordCounter/" + curr_channel  + "/" + date_time + "__WordCount.txt")

    s3_res.meta.client.upload_file("./web_data/web_data_file_names.txt", bucket_name, "InstanceSetup/web_data/web_data_file_names.txt")


   



def CatFormmatedString(channel, stream_start_time, p_n, cat_dict):

    #t_c_info = ReadFile("./TitleCategoryInfo/" + "FINAL" + channel +  "TitleCategoryInfo.txt")

    try:
        #cat_dict = t_c_info[p_n]["category_change_dict"]
        formatted_cat_dict = GetTimeFormattedCat(cat_dict, stream_start_time)
    
    except:
        formatted_cat_dict = "no data"
    return formatted_cat_dict
    
    



def GetActiveVC():
    vc_all = ReadFile("comms_view_count_info.txt")
    active_channels = []
    for channel in constants_2["channels"]:
        if vc_all[channel] == []:
            continue
        else:
            active_channels.append({channel : vc_all[channel]})
    return active_channels



def GetTimeDateStr():
    return datetime.today().strftime('%Y-%m-%d-%H-%M-%S')


def getLiveStatusList():
    channel_list = constants_2["channels"]
    

    live_status_list = {}
    for channel in channel_list:
        temp = getViewerCount(channel)
        if type(temp) == int:
            live_status_list[channel] = temp
        else:
            live_status_list[channel] = "offline"

    return live_status_list

def getHeaders():
    return {"client-id": constants_2["botClientId"], "Authorization": "Bearer " +  constants_2["botAuth"]}



def sendEmail(sender_email, sender_password, receiver_email, message):

    

    port = 465  # For SSL

    context = ssl.create_default_context()

    server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
    server.login(sender_email, sender_password)

    #server.sendmail(sender_email, receiver_email, message)

def WaitToTime(t_w):
    print("wait time start", t_w - time() + 1)
    sleep(t_w - time() + 1)
    print("wait time end")


def getUserID(chatter):

    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/users?login=" + chatter)

    try: 
        user_id = jsoninfo["data"][0]["id"]
        return user_id
    except:
        print("USER ID, err") 
        return "no id"

def graphData(graph_data, current_dateF1_start, current_time_start, channel, ext):

    export_data = zip_longest(*graph_data[channel].values(), fillvalue = '')
 
    date = current_dateF1_start.replace("/", "-")
    time = current_time_start
    filename = channel + "_" + date + "_" + "at" + "_"  + time + ext +  ".csv"
    with open(filename, 'w', encoding="ISO-8859-1", newline='') as file:
        write = csv.writer(file)
        write.writerow(graph_data[channel].keys())
        write.writerows(export_data)


def TwitchRequest(url):
    

    while True:
        try:
            info = requests.get(url, headers= getHeaders())
            break
            
        except:
            print("couldn't get INFO")
            sleep(5)
            
            



    if info.status_code != 200:
        try:
            if int(info.headers["Ratelimit-Remaining"]) == 0:
                t_reset = int(info.headers["Ratelimit-Reset"])
                print("reached lim", info.status_code, "waiting:", t_reset - time())
                try:
                    WaitToTime(t_reset)
                except:
                    TwitchRequest(url)
                TwitchRequest(url)
            elif info.status_code == 429:
                print("429 but no detected 0 rate lim. rate lim:", info.headers["Ratelimit-Remaining"])
                TwitchRequest(url)
            
            else:
                print("other err", info.status_code, int(info.headers["Ratelimit-Remaining"]))
                sleep(3)
                TwitchRequest(url)
        except:
            sleep(3)
            
            print("RARE RATELIM KEY ERR", info.status_code, info.text)
            TwitchRequest(url)

    if info.status_code != 200:
        print("PAST TwitchRequest")
        sleep(5)
        TwitchRequest(url)
    
    else:
        try:
            res = json.loads(info.text)
            if res == None:
                print("NONE")
                sleep(2)
                TwitchRequest(url)
            else:
                return res
        except:
            print("ERR IN TwitchRequestm, none test failed")
            sleep(2)
            TwitchRequest(url)



def GetDisplayName(channel):
    supported_channels_dict = {"nmplol" : "Nmplol" ,"mizkif" :  "Mizkif", "asmongold" :  "Asmongold", "hasanabi" : "HasanAbi","jinnytty" :  "Jinnytty", "xqc" : "xQc", "maya" : "Maya", "emiru" : "Emiru", "ibai" : "ibai", "rubius" : "Rubius", "pokimane" : "pokimane", "tubbo" : "Tubbo", "brucedropemoff" : "BruceDropEmOff", "loltyler1" : "loltyler1", "sodapoppin" : "sodapoppin", "ironmouse" : "ironmouse", "moistcr1tikal" : "moistcr1tikal", "mitchjones" : "MitchJones","lirik" :  "LIRIK", "forsen" : "forsen", "botezlive" : "BotezLive", "imkaicenat" : "ImKaiCenat", "jerma985" : "Jerma985", "adinross" : "AdinRoss","yoitsm8in34yoitsm8in34" : "yoitsm8in34yoitsm8in34"}
    return supported_channels_dict[channel]

    
def SaveTTVC(channel, TCT_bool):
    
    try:
        
        f =ReadFile("./TTVC/" +  channel + "_TTVC.txt")
    except:
        
        WriteFile("./TTVC/" +  channel + "_TTVC.txt", {})
        f =ReadFile("./TTVC/" +  channel + "_TTVC.txt")

    req_url = "https://api.twitch.tv/helix/streams/?user_login=" + channel
    jsoninfo = TwitchRequest(req_url)
    #print(jsoninfo)
    while jsoninfo == None:
        sleep(10)
        print("NONE 695", jsoninfo)
        jsoninfo = TwitchRequest(req_url)

    if jsoninfo == None:
        sleep(5)
        SaveTTVC(channel, TCT_bool)
    try:
        if jsoninfo["data"] == []:
            return False
    except:
        print("NONE ERROR 2")
        print(data)
        sleep(5)
        SaveTTVC(channel, TCT_bool)
    
    while True:
        try:
            data = jsoninfo["data"][0]
            break
        except:
            print("NONE ERROR 3")
            print(data)
            sleep(10)
            SaveTTVC(channel, TCT_bool)

    t = int(time() * 1000)
    f["VC_dict"]["times"].append(t)
    f["VC_dict"]["views"].append(int(data["viewer_count"]))
    

    if TCT_bool:
        SaveCurrThumbnail(channel, data["thumbnail_url"])
        TC_d = {t : { "title" : data["title"], "category" : data["game_name"]}}
        start_time = data["started_at"]

        if len(f["api_start_time_str"]) == 0:
            f["api_start_time_str"].append(start_time)
        
        elif start_time != f["api_start_time_str"][-1]:
            f["api_start_time_str"].append(start_time)
        
        f["TC_dict"].update(TC_d)
            
    
    
    WriteFile("./TTVC/" +  channel + "_TTVC.txt", f)

    return True



def ResetTTVC(channel):
    print("reseting TTVC", channel)
    WriteFile("./TTVC/" +  channel + "_TTVC.txt", {"VC_dict" : {"times" : [], "views" : [] }, "TC_dict" : {}, "api_start_time_str" : ""} )


def getThumbnailURL(channel):
    


    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/streams/?user_login=" + channel)


    if jsoninfo["data"] == [] or jsoninfo["data"][0]["viewer_count"] == "s":
        #print(channel + " is offline")
        return ["offline", "no thumbnail"]
    viewer_count = jsoninfo["data"][0]["viewer_count"]
    thumbnail = jsoninfo["data"][0]["thumbnail_url"]
    #print("viewer count: ", viewer_count)
    return thumbnail

def getViewerCount(channel):

    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/streams/?user_login=" + channel)


    if jsoninfo["data"] == [] or jsoninfo["data"][0]["viewer_count"] == "s":
        #print(channel + " is offline")
        return ["offline", "no thumbnail"]
    viewer_count = jsoninfo["data"][0]["viewer_count"]
    return viewer_count

def AddToNewFollowingInfo(username, channel, id, following_status_date, new_following_list, prev_info):
    
    if following_status_date == "not following":
        
        return new_following_list

    if prev_info != None:


        prev_info.update({channel : following_status_date})
        new_following_list.append({username : prev_info})
    else:
        new_following_list.append({username : {"id" : id, channel : following_status_date}})

    return new_following_list


def UpdateChatterInfo(chatter_follower_info, new_following_list):
    #print("num of new followers to add:", len(new_following_list))
    for d_pair in new_following_list:
        chatter_follower_info.update(d_pair)
    return chatter_follower_info


def SingFollowingInfo(msg, new_following_list, chatter_follower_info, channel_id):
    if msg["username"] in chatter_follower_info:
        if msg["channel"] in chatter_follower_info[msg["username"]]:
            follow_status_date = chatter_follower_info[msg["username"]][msg["channel"]]            
            return follow_status_date, new_following_list


        else:
            chatter_prev_info = chatter_follower_info[msg["username"]]
            if channel_id == "no id":
                print("no id", msg["username"])
                return "not following", new_following_list
            
            following_status_date =  GetFollowEpochTime(msg["id"], channel_id)
            new_following_list = AddToNewFollowingInfo(msg["username"], msg["channel"], msg["id"], following_status_date, new_following_list, chatter_prev_info)
            return following_status_date, new_following_list
    else:
        
        
        if channel_id == "no id":
            return "not following", new_following_list  
            
        following_status_date =  GetFollowEpochTime(msg["id"], channel_id)
        new_following_list = AddToNewFollowingInfo(msg["username"], msg["channel"], msg["id"], following_status_date, new_following_list, None)
        return following_status_date, new_following_list


def GetCurrDateF2():
    today = date.today()
    current_dateF1 = today.strftime("%Y/%m/%d")
    current_dateF2 = [current_dateF1[:4], current_dateF1[5:7], current_dateF1[8:]]
    return current_dateF2




    
    

        


def TimeSortedAnalysis(time_sorted_msg, channel_id, chatter_follower_info, curr_time_ms):
    curr_time_epoch_sec = int(curr_time_ms/1000)



    #print("start slot analysis")
    if len(time_sorted_msg) < 1:

        #print("0 msgs in time slot")


        res = {"num_msg" : 0, "sub_percentage" : 0, "sub_avg_len" : 0, "following_percentage" : 0, "follower_avg_len" : 0, "unique_chatter_ratio" : 0, "similarity_level" : 0, "emote_moment" : None, "first_msg_num" : 0, "emote_percentage" : 0}

        return res, []


    num_msg = len(time_sorted_msg)
    new_following_list = []
    #print("msg1", time_sorted_msg[1])

    #sub %
    #sub len
    sub_count = 0
    sub_len_tot = 0
    for msg in time_sorted_msg:
        if msg["sub"]:
            sub_count += 1
            try:
                sub_len_tot += int(list(msg["sublen"].values())[0])
            except:
                sub_len_tot += 0

        
    sub_percentage = (sub_count/num_msg) * 100
    if sub_count == 0:
        sub_avg_len = 0
    else:
        sub_avg_len = sub_len_tot/sub_count

    #follower %
    
    #follower len
    follower_count = 0
    follower_len_tot = 0
    for msg in time_sorted_msg:
        following_status_date, new_following_list_n = SingFollowingInfo(msg, new_following_list, chatter_follower_info, channel_id)
        if following_status_date != "not following":
            delta_sec = curr_time_epoch_sec - following_status_date
            if delta_sec >= 0:
                time_since_follow_months = delta_sec/2629800 #3600 * 24 * 30.4375
                follower_count += 1
                follower_len_tot += time_since_follow_months


    print("num of new followers:", channel_id, len(new_following_list_n))


    
    following_percentage = (follower_count/num_msg) * 100
    if follower_count == 0:
        follower_avg_len = 0
    else:
        follower_avg_len = follower_len_tot/follower_count

    unique_chatter_count = 0
    chatter_list = []
    
    for msg in time_sorted_msg:
        chatter_list.append(msg["username"])
    

    unique_chatter_count = len(list(dict.fromkeys(chatter_list).keys()))
    unique_chatter_percentage = (unique_chatter_count/num_msg) * 100


    
    msg_list = [msg["message"] for msg in time_sorted_msg]
    similarity_level = similarityScore(msg_list, comparaison_per_msg=1, similarity_threshold=0.5, num_similarity_threshold=0.2)
    
    top_emotes_dict = GetTopEmoteTotall(time_sorted_msg)
    if top_emotes_dict == None:
        print("emotes moment 855 NONE")
        emote_moment = None
    else:
        emote_moment = top_emotes_dict[0][0]
    emote_percentage = GetEmotePercentage(time_sorted_msg)




    first_msg_num = GetFirstMsgNum(time_sorted_msg)
    

    res = {"num_msg" : num_msg, "sub_percentage" : round(sub_percentage, 2), "sub_avg_len" : round(sub_avg_len, 2), "following_percentage" : round(following_percentage, 2), "follower_avg_len" : round(follower_avg_len, 2), "unique_chatter_ratio" : round(unique_chatter_percentage, 2), "similarity_level" : round(similarity_level, 2), "emote_moment" : emote_moment, "emote_percentage" : emote_percentage, "first_msg_num" : first_msg_num}

    #old
    #return res, chatter_follower_info
    #New


    return res, new_following_list_n

def GetFirstMsgNum(time_sorted_msg):
    count = 0
    for msg in time_sorted_msg:
        if msg["first_msg"]:
            count += 1
    return count


def SortedMsgListsPerTime(all_data, times_list, time_delta):
    channel_sorted_list = all_data
    time_sorted_msg = {}
    for t_lim in times_list:
        time_sorted_msg[t_lim] = []
        for msg in channel_sorted_list:
            if int(msg["time"]) < t_lim and int(msg["time"]) > (t_lim - time_delta):
                time_sorted_msg[t_lim].append(msg)
    return time_sorted_msg

def GetTimesList(all_data, time_delta):
    print("IN GETTIMES LIST")
    initial_time = int(all_data[0]["time"])
    final_time = int(all_data[-1]["time"])
    print(initial_time)
    print(final_time)

    times_list = []
    t = initial_time
    while t < final_time - time_delta:
        t += time_delta
        times_list.append(t)

    
    print("len of times list", len(times_list))
    return times_list





def GetNumMsgsPerXTopChattersAndPopularColors(all_data, arr):
        #sort by to chatters, from 1 to 100 lets try
    
    
    num_msg_per_x_top_chatters_list = []

    chatter_msg_count_dict = {}
    color_occ_dict = {}
    all_channel_msgs = all_data

    msg_count = len(all_channel_msgs)

    for msg in all_channel_msgs:
        username = msg["username"]
        color = msg["color"]

        if username in list(chatter_msg_count_dict.keys()):
            chatter_msg_count_dict[username] += 1
        else:
            chatter_msg_count_dict[username] = 1
        
        if color in list(color_occ_dict.keys()):
            color_occ_dict[color] += 1
        else:
            color_occ_dict[color] = 1
    
    sorted_top_chatters_num_list = MergSort(list(chatter_msg_count_dict.values()))[::-1]

    r = dict(sorted(color_occ_dict.items(), key=lambda item: item[1]))
    sorted_color_list_sub_20 =  [list(r.keys())[::-1][:20], list(r.values())[::-1][:20]]



    for v in arr:
        num_of_chatters = int(v * len(list(chatter_msg_count_dict.keys())))
        temp = sum(sorted_top_chatters_num_list[:num_of_chatters])
        num_msg_per_x_top_chatters_list.append(round( (temp/msg_count) * 100, 2) )
    


    return num_msg_per_x_top_chatters_list, sorted_color_list_sub_20


def GetTopEmoteMoments(analysis_all):

    emote_moments_list = [x["emote_moment"] for x in analysis_all.values()]

    cnt = Counter(emote_moments_list)
    res = dict(cnt)
    r = dict(sorted(res.items(), key=lambda item: item[1]))
    return [list(r.keys())[::-1], list(r.values())[::-1]]

    # cnt = Counter()
    # for e_name in top_emote_name_list:
    #     cnt[e_name] += 1

    # res = dict(cnt)
    # r = dict(sorted(res.items(), key=lambda item: item[1]))
    # return [list(r.keys())[::-1], list(r.values())[::-1]]

def GetTopEmoteTotall(all_data):
    res = EmoteOccurenceDict(all_data)
    if res == None:
        print("EMOTES TOP ALL NO EMOTES")
        return None
    r = dict(sorted(res.items(), key=lambda item: item[1]))
    return [list(r.keys())[::-1], list(r.values())[::-1]]
    





def GetAnalysisAll(all_data, channel, times_list, time_delta):
    print("START ANALYSIS")
    analysis_all = {} 
    i = 0
    


    channel_id = getUserID(channel)

    

    all_msg_in_time_slots = SortedMsgListsPerTime(all_data, times_list, time_delta)
    print("num of divisions", len(all_msg_in_time_slots))

    all_msg_content_list = [[msg["message"] for msg in t_slot] for t_slot in all_msg_in_time_slots.values()]
    final_word_dict = GetFinalWordDict(all_msg_content_list)
    
    while True:
        try:
            chatter_follower_info = ReadFile("chatter_info.txt")
            break
        except:
            print("CANT READ CHATTER INFO", time())
            sleep(1)
    
    need_f_info_list = []
    for time_sorted_list in all_msg_in_time_slots.values(): 
        analysis_all[times_list[i]], new_chatter_following_list = TimeSortedAnalysis(time_sorted_list, channel_id, chatter_follower_info, times_list[i])

        need_f_info_list.extend(new_chatter_following_list)


        i += 1
    
    print("END ANALYSIS")
    return analysis_all, need_f_info_list, final_word_dict



def GetNormalDataInOrderDict(analysis_all, times_list):
    all_normal_keys = [k for k in list(analysis_all[times_list[0]].keys())]
    all_normal_keys.remove("emote_moment")
    
    normal_data_in_order_list = GetListInAnalysisAll(analysis_all, all_normal_keys) 
    normal_data_in_order_dict = {}
    i = 0
    for k in all_normal_keys:
        normal_data_in_order_dict[k] = normal_data_in_order_list[i]
        i += 1
    return normal_data_in_order_dict


def GetListInAnalysisAll(analysis_all, key_list):
    times_list = list(analysis_all.keys())
    res = []
    
    for key in key_list:
        res.append([analysis_all[time_t][key] for time_t in times_list])
    return res



def GetTimeSeconds(start_time, time):
    return int(((time - start_time)/1000))

def GetTimeMinutes(start_time, time):
    return round(GetTimeSeconds(start_time, time)/60 , 1)

def GetTimeListSeconds(times_list):
    start_time = times_list[0]
    new_time_list = []
    for time in times_list:
        new_time_list.append(GetTimeSeconds(start_time, time))
    return new_time_list

def GetTimeListMinutes(times_list):
    start_time = times_list[0]
    new_time_list = []
    for time in times_list:
        new_time_list.append(GetTimeMinutes(start_time, time))
    return new_time_list



def Merge(l1, l2):
    
    if len(l1) > len(l2):
        la = l1
        lb = l2
    else:
        la = l2
        lb = l1
    res = []
    while len(lb) > 0 and len(la) > 0: 
        if la[0] > lb[0]:
            res.append(lb[0])
            lb.pop(0)
        else:
            res.append(la[0])
            la.pop(0)
    while len(lb) > 0:
        res.append(lb[0])
        lb.pop(0)
    while len(la) > 0:
        res.append(la[0])
        la.pop(0)
    
    return res



def MergSort(list):
    if len(list) < 2:
        return list
    else:
        mid = int(len(list)/2)
        l1 = list[:mid]
        l2 = list[mid:]
        
        l1 =  MergSort(l1)
        l2 = MergSort(l2)
        return Merge(l1, l2)






def NumOfOccurences(emote, msg_list):
    #ignores multiple emotes in same msg
    count = 0
    for msg in msg_list:
        if emote   in msg:
            count += 1
    return count

def EmoteOccurenceDict(msg_list_full):
    emote_id_list = []
    for msg in msg_list_full:
        if msg["emote_info"] != None:
            for emote in msg["emote_info"].keys():
                emote_id_list.append(emote)
    if emote_id_list == []:
        return None
    c = Counter(emote_id_list)
    return dict(c)


def GetStreamStartTime(channel):
    req_url = "https://api.twitch.tv/helix/streams/?user_login=" + channel
    jsoninfo = TwitchRequest(req_url)
    data = jsoninfo["data"][0]
    t = data["started_at"]
    print("RAW time",t)
    y =  t[:10]
    conc = t[:10] + " " + t[11:-1]
    
    t_e = GetEpochTime(conc)
    return int(t_e * 1000) 

def GetEpochTime(t_str):
    # e_t = timegm(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))
    e_t = timegm(strptime(t_str, '%Y-%m-%d %H:%M:%S'))
    return e_t
def RetrieveStartTimeMs(api_t_str):
    conc = api_t_str[:10] + " " + api_t_str[11:-1]
    #print("conc", conc)
    return int(GetEpochTime(conc) * 1000)

def GetStartTimeFromEndTime(start_time_str_list, end_time):
    start_time_epoch_list = [RetrieveStartTimeMs(x) for x in start_time_str_list]
    diff_dict = {x : end_time - x for x in start_time_epoch_list}
    for k in list(diff_dict.keys()):
        if diff_dict[k] < 0:
            diff_dict.pop(k)

    start_time_good_val = min(diff_dict.values())

    for x in diff_dict.keys():
        if diff_dict[x] == start_time_good_val:
            start_time_epoch = x

    return start_time_epoch


def GetFollowEpochTime(user_id, channel_id):
    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/users/follows?from_id=" + user_id + "&to_id=" + channel_id + "&first=" + "1")
    if jsoninfo == None:
        print("NONE TPE APIFOLLOW 1161", user_id, channel_id)
        return "not following"
    if jsoninfo["data"] == []:
        return "not following"
    else:
        try:
            followed_date = jsoninfo["data"][0]["followed_at"]
            utc_time = strptime(followed_date, "%Y-%m-%dT%H:%M:%SZ")
            epoch_time = timegm(utc_time)
            return epoch_time
        except:
            print("D0 ERROR with", user_id, channel_id)
            return "not following"
    

def GetGlobalEmotes():

    jsoninfo = TwitchRequest("https://api.twitch.tv/helix/chat/emotes/global")

def saveFollowingInfo(x, chatter_info, channel):
    print("start following info")
    channel_id = x[0]
    chatter_list = x[1]

    for chatter in chatter_list:
        jsoninfo = TwitchRequest("https://api.twitch.tv/helix/users/follows?from_id=" + chatter_info[chatter]["id"] + "&to_id=" + channel_id + "&first=" + "1")
        if jsoninfo["data"] == []:
            chatter_info[chatter][channel] = "not following"

        else:  
            followed_date = jsoninfo["data"][0]["followed_at"]
            print(followed_date)
            utc_time = strptime(followed_date, "%Y-%m-%dT%H:%M:%SZ")
            epoch_time = timegm(utc_time)
            chatter_info[chatter][channel] = epoch_time

    print("end following info")


def similarityScore(str_list, comparaison_per_msg, similarity_threshold, num_similarity_threshold):
    return 0


def ConvertPageNames(p_n, start_time, end_time):
    arr = p_n.split("_")
    year = arr[0]
    month = int(arr[1]) - 1
    day = arr[2]

    months_arr = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


    start_hour = strftime('%H', localtime(start_time/1000))
    end_hour = strftime('%H', localtime(end_time/1000))

    hours_str_list = []
    for hour_str in [start_hour, end_hour]:
        print("hour_str", hour_str)
        hour = int(hour_str)

        if hour < 12:
            res = str(hour) + "AM"
        
        elif hour == 12:
            res = "12PM"

        elif hour > 12:
            res = str(hour - 12) + "PM"
        print("res", res)
        hours_str_list.append(res)
    
    return months_arr[month] + " " + day + "th, " + year  + ". " + hours_str_list[0] + "-" + hours_str_list[1]


def GetTimeFormattedCat(categories_change_dict, stream_start_time):
    print("1458 CAT DICT1", categories_change_dict)
    new_dict = {}
    for t in  list(categories_change_dict.keys()):
        s =  GetTimeHourMinFormat(int(t) - stream_start_time)
        s_2 = s[0:-2]
        s_2 += "00"
        new_dict[s] = categories_change_dict[t] 

    print("1466 CAT DICT RETURN", new_dict)
    return new_dict

def GetTimeHourMinFormat2(t):

    sec = t - math.floor(t)
    sec_i = int(sec * 60)
    if (sec_i == 60):
        sec_i = 0
    
    sec_s = ""
    if sec_i < 10:
        sec_s = "0" + str(sec_i)
    
    else:
        sec_s = str(sec_i)
    

    t = int(t)

    min  = t % 60
    min_s = ""
    if (min < 10):
        min_s = "0" + str(min) + ":"
    
    else:
        min_s = str(min)  + ":"
    
    t_2 = t - min

    hour_s = ""
    if t_2 != 0:
        hour = int(t_2/60)
        hour_s = str(hour) + ":"

    return hour_s + min_s + sec_s

def GetTimeHourMinFormat_MM(t_ms):
    return timedelta(seconds=int(t_ms/1000))





def GetNThumbnailsList(n, diff_list, channel, start_time, end_time):
    start_time = int(start_time/1000)
    end_time = int(end_time/1000)
    length = end_time - start_time


    t_i_list = []
    for i in range(n):
        t_i_list.append(int(start_time  + diff_list[i] * length))
    
    
    
    t_files_list = os.listdir("Thumbnails/" + channel + "/")


    if len(t_files_list) < n:
        return {"file_names" : None, "labels" : None}
    

    t_times_list = []
    for f_n in t_files_list:
        l1 = f_n.split("__")
        t = int(l1[0])
        t_times_list.append(t)
        
    if t_times_list[-1] < t_i_list[0]:
        print("p1 1524")
        return {"file_names" : None, "labels" : None}
    
    thumbnail_times_list = []
    
    i = 0
    for j in range(n):
        while i < len(t_times_list) and j < len(t_i_list) and t_times_list[i] < t_i_list[j]:
            i += 1

        if i == len(t_times_list):
            break
        else: 
            thumbnail_times_list.append(t_times_list[i])

    #print("p2 1376", thumbnail_times_list, len(thumbnail_times_list))

    final_f_n_list = []
    labels_list = []
    
    for f_n in t_files_list:
        l1 = f_n.split("__")
        t = int(l1[0])
        

        for i in range(len(thumbnail_times_list)):
            if t == thumbnail_times_list[i]:
                labels_list.append(GetTimeHourMinFormat( (t - start_time)/60)  ) 
                final_f_n_list.append(f_n)
                
    return {"file_names" : final_f_n_list, "labels" : labels_list}

def Get3ThumbnailsList(channel):
    thumbnails_dict = {}
    web_data_streams_info = ReadFile("./web_data/web_data_file_names.txt")

    p_n_list = list(web_data_streams_info[channel].keys())

    if len(p_n_list) == 0:
        return None
    
    for p_n in p_n_list:
        start_time = web_data_streams_info[channel][p_n]["stream_start_time"]
        end_time = web_data_streams_info[channel][p_n]["stream_end_time"]
        
        range_diff_list = [0.2, 0.5, 0.8]
        l_1 =  GetNThumbnailsList(3, range_diff_list, channel, start_time, end_time)
        l = l_1["file_names"]

        if l == None:
            continue

        thumbnails_dict[p_n] = l
    
    return thumbnails_dict




def AvgNPlaces(v_l):
    sum = 0
    for i in range(len(v_l)):
        sum += v_l[i]
    
    return round((sum/len(v_l)), 2)

def GetAveragedWebDataN(n, web_data):
    n_w_d_k = {}
    
    w_d_keys = web_data["keys"]

    for key in list(w_d_keys.keys()):
        n_w_d_k[key] = []
        i = 0
        while(i + n < len(w_d_keys[key])):
            v_list = []
            for j in range(n):
                v_list.append(w_d_keys[key][i + j])
            avg_v = AvgNPlaces(v_list)

            for j in range(n):
                n_w_d_k[key].append( str(avg_v))
            i+= n

        while i < len(w_d_keys[key]):
            n_w_d_k[key].append(w_d_keys[key][i])
            i += 1

    return n_w_d_k


def GetTimeHourMinFormatList(t_list):
    
    res_list = []
    for t in t_list:
        res_list.append(GetTimeHourMinFormat(t))
    
    return res_list

def GetTimeHourMinFormat(t):

    sec = t - math.floor(t)
    sec_i = int(sec * 60)
    if (sec_i == 60):
        sec_i = 0
    
    sec_s = ""
    if (sec_i < 10):
        sec_s = "0" + str(sec_i)
    
    else:
        sec_s = str(sec_i)
    
    t = int(t)

    min  = t % 60
    min_s = ""
    if (min < 10):
        min_s = "0" + str(min) + ":"
    
    else:
        min_s = str(min)  + ":"
    
    t_2 = t - min

    hour_s = ""
    if (t_2 != 0):
        hour = int(t_2/60)
        
        hour_s = str(hour) + ":"

    return hour_s + min_s + sec_s


def GetStreamResults(web_data_normal_keys, stream_len_hour):
    w_d_k = web_data_normal_keys
    avg_d = {}
    for key in list(w_d_k.keys()):
        #print(key, w_d_k[key])
        list_sum = sum(w_d_k[key])

        avg =  round(  list_sum/len(w_d_k[key]) , 2)
        avg_d[key] = avg

    avg_d["sub_follow_diff"] = round( avg_d["follower_avg_len"] -  avg_d["sub_avg_len"], 2)


    avg_d["tot_bans_num"] = round( sum(w_d_k["bans_num"])/stream_len_hour , 2)
    avg_d["tot_timeout_num"] = round(sum(w_d_k["timeout_num"])/stream_len_hour, 2)
    avg_d["tot_deleted_msgs_num"] = round( sum(w_d_k["deleted_msgs_num"])/stream_len_hour, 2)
    avg_d["tot_first_msg_num"]=  round( sum(w_d_k["first_msg_num"])/stream_len_hour, 2 )

    return avg_d


def GetWordDict(msg_l):
    all_d = {}
    for msg in msg_l:
        w_l = msg.split()
        curr_d = Counter(w_l)
        
        for items in curr_d.items():
            if items[0] in all_d:
                all_d[items[0]] += items[1]
            else:
                all_d[items[0]] = items[1]
    return all_d


def GetFinalWordDict(all_time_slots):
    final_dict = {}
    slot_i = 0
    for t_slot in all_time_slots:
        d = GetWordDict(t_slot)
        #print("SLOT COUNT DICT", slot_i, d)
        commun = []
        new = []
        
        for w in d:
            if w in final_dict:
                commun.append(w)
            else:
                new.append(w)
        for commun_w in commun:
            final_dict[commun_w][slot_i] = d[commun_w]
        for new_w in new:
            final_dict[new_w] = {}
            final_dict[new_w][slot_i] = d[new_w]

        slot_i += 1
    
    for w in list(final_dict.keys()):
        if sum(final_dict[w].values()) < 5:
            final_dict.pop(w)
    return final_dict
