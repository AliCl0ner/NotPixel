import os
import threading
import asyncio
from bot.painter import painters
from bot.mineclaimer import mine_claimer
from bot.utils import night_sleep, Colors
from bot.notpx import NotPx
import config
from telethon.sync import TelegramClient

def multithread_starter():
    dirs = os.listdir("sessions/")
    sessions = list(filter(lambda x: x.endswith(".session"),dirs))
    sessions = list(map(lambda x: x.split(".session")[0],sessions))
    for session_name in sessions:
        try:
            cli = NotPx("sessions/"+session_name)
            threading.Thread(target=painters,args=[cli,session_name]).start()
            threading.Thread(target=mine_claimer,args=[cli,session_name]).start()
        except Exception as e:
            print("[!] {}Error on load session{} \"{}\", error: {}".format(Colors.RED,Colors.END,session_name,e))
def process():
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    print(r"""{}
    _   _       _  ______       ______       _   
    | \ | |     | | | ___ \      | ___ \     | |  
    |  \| | ___ | |_| |_/ /_  __ | |_/ / ___ | |_ 
    | . ` |/ _ \| __|  __/\ \/ / | ___ \/ _ \| __|
    | |\  | (_) | |_| |    >  <  | |_/ / (_) | |_ 
    \_| \_/\___/ \__\_|   /_/\_\ \____/ \___/ \__|                                  
            NotPx Auto Paint & Claim by AliCloner - v1.0 {}""".format(Colors.BLUE, Colors.END))

    while True:
        option = input("[!] {}Enter 1{} For Adding Account and {}2 for start{} mine + claim: ".format(Colors.BLUE, Colors.END, Colors.BLUE, Colors.END))
        if option == "1":
            name = input("\nEnter Session name: ")
            if not any(name in i for i in os.listdir("sessions/")):
                client = TelegramClient("sessions/" + name, config.API_ID, config.API_HASH).start()
                client.disconnect()
                print("[+] Session {} {}saved successfully{}.".format(name, Colors.GREEN, Colors.END))
            else:
                print("[x] Session {} {}already exists{}.".format(name, Colors.RED, Colors.END))
        elif option == "2":
            multithread_starter()
            break
