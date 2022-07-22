require('dotenv').config();

const fs = require('fs') 
const tmi = require('tmi.js');


export function WriteFileJS(file_name, data){
    let data_a = JSON.stringify(data)
    fs.writeFileSync(file_name, data_a, (err) => { 
        if (err) throw err; 
    }) 
}
export function ReadFileJS(file_name){
    var data_r = fs.readFileSync(file_name, "utf-8")
    var data = JSON.parse(data_r)
    return data
}
function GetTimeDate(){
var today = new Date();
var date = today.getFullYear()+'_'+(today.getMonth()+1)+'_'+today.getDate();
var time = today.getHours() + "_" + today.getMinutes() + "_" + today.getSeconds();
var dateTime = date+'_'+time;

    return dateTime
}


const constants_2 = ReadFileJS("constants.txt")
const channels = constants_2["channels"]
const channels_raw = [...channels]
const modUsername = constants_2["modUsername"]
const update_time = constants_2["update_time"]
const minimum_msgs = constants_2["minimum_msgs"]



const client = new tmi.Client({
    options: { debug: true, messagesLogLevel: "info" },
	connection: {
        reconnect: true,
		secure: true
	},
	identity: {
        username: constants_2["botUsername"],
        password: constants_2["botAuth"]
        
	},
    channels: channels
});



function sleep(seconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < (1000 *seconds));
}

var past_data = ReadFileJS("curr_chat_data.txt")

if (past_data == ""){

var msg_info_list = {}
msg_info_list["timeout_info"] = {}
msg_info_list["deleted_msgs"] = {}
msg_info_list["bans"] = {}
for (let channel of channels_raw){
    msg_info_list[channel] = []   
    msg_info_list["timeout_info"][channel] = []
    msg_info_list["deleted_msgs"][channel] = []
    msg_info_list["bans"][channel] = []
}

}
else{
    msg_info_list = past_data
    
}

var time_done = false
var msg_counter = 0



WriteFileJS("comms_need_save_view_count.txt", ["normal", []])


function SaveCheck(msg_info_list){
    WriteFileJS("curr_chat_data.txt", msg_info_list)

    let comms_save_d = {}
    
    let txt_r = ReadFileJS("comms_need_save_view_count.txt")
    let txt_0 = txt_r[0]
    let txt = txt_r[1]
    console.log("IN SAVE CHECK")
    let saved_once = false
    let past_normal = false

    console.log(txt_0, txt)

    if (txt_0 != "normal"){
        past_normal = true
        console.log("PAST NORMAL")
        for(const channel in txt){
            if (txt[channel] && msg_info_list[channel].length >= minimum_msgs){
                console.log("PAST SAVE CHECK")
            // if (txt[channel] == "save" && msg_info_list[channel].length > 200 ){
                console.log("start of saving:", channel)
                console.log(msg_info_list[channel].length)
                let date_time = GetTimeDate()
                let file_name = "all_data_" + date_time + channel + ".txt" 
                WriteFileJS("./all_data/" + file_name, {"normal_all_data" : msg_info_list[channel],"timeout_info" : msg_info_list["timeout_info"][channel], "deleted_msgs" : msg_info_list["deleted_msgs"][channel], "bans" : msg_info_list["bans"][channel]})
    3
    
                comms_save_d[channel] = [file_name, date_time]
                
                msg_info_list[channel] = []
                msg_info_list["timeout_info"][channel] = []
                msg_info_list["deleted_msgs"][channel] = []
                msg_info_list["bans"][channel] = []
    
                saved_once = true

    }
            
            
            
            
        }
    }
    if(saved_once){
        console.log("SAVED ONCE")
        while(true){
            try {
                WriteFileJS("comms_need_save_view_count.txt", ["js just saved", comms_save_d])
                break
                
            } catch (error) {
                console.log("ERR, trying to read/write at same time")
                sleep(0.1)                
            }
        }
        console.log("RESET MSG LIST")
        return msg_info_list 
        
    }
    else{
        if(past_normal){
            WriteFileJS("comms_need_save_view_count.txt", ["Failed save requirement", []])
            
            return msg_info_list 
        }
        return msg_info_list 
        
    }
}



var offlineMode = false

time_done = false

setInterval(function(){ time_done = true }, update_time*1000);




client.connect().catch(console.error);
client.on('message', (channel, tags, message, self) => {
	// if(self) return;
	// console.log(channel, message);
    msg_counter += 1
    
    var channel = channel.substring(1)
    msg_info_list[channel].push({"channel": channel, "username" : tags["username"], "id" : tags['user-id'], "message" : message, "sub" : tags.subscriber, "sublen": tags['badge-info'], "time" : tags["tmi-sent-ts"], "first_msg" : tags["first-msg"], "emote_info" : tags["emotes"], "color" : tags["color"]})
    
    
    
    //console.log(msg_info_list)

    
    
    
//get first msgs as well
    
    if (time_done && msg_counter > 1 && offlineMode == false){
        msg_info_list =  SaveCheck(msg_info_list)
        time_done = false
    }
}); 

client.on("timeout", (channel, username, reason, duration, userstate) => {
    console.log(userstate["tmi-sent-ts"])
    msg_info_list["timeout_info"][channel.substring(1)].push({"ban-duration" : duration,"reason" : reason, "time" : userstate["tmi-sent-ts"]}) 
    // Do your stuff.
});

client.on("messagedeleted", (channel, username, deletedMessage, userstate) => {
    msg_info_list["deleted_msgs"][channel.substring(1)].push(userstate["tmi-sent-ts"]) 
    
});



client.on("ban", (channel, username, reason, userstate) => {
    msg_info_list["bans"][channel.substring(1)].push(userstate["tmi-sent-ts"]) 
    
});