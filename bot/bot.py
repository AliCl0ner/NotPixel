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
    sessions = list(filter(lambda x: x.endswith(".session"), dirs))
    sessions = list(map(lambda x: x.split(".session")[0], sessions))
    
    for session_name in sessions:
        try:
            cli = NotPx("sessions/" + session_name)

            # Define a wrapper function to run the async function in the thread
            def run_painters():
                asyncio.run(painters(cli, session_name))

            def run_mine_claimer():
                asyncio.run(mine_claimer(cli, session_name))

            # Start threads for painters and mine_claimer
            threading.Thread(target=run_painters).start()
            threading.Thread(target=run_mine_claimer).start()
        except Exception as e:
            print("[!] {}Error on load session{} \"{}\", error: {}".format(Colors.RED, Colors.END, session_name, e))

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
        # option = "2"
        if option == "1":
            name = input("\nEnter Session name: ")
            if not any(name in i for i in os.listdir("sessions/")):
                client = TelegramClient("sessions/" + name, config.API_ID, config.API_HASH).start()
                client.disconnect()
                print("[+] Session {} {}saved success{}.".format(name, Colors.GREEN, Colors.END))
            else:
                print("[x] Session {} {}already exist{}.".format(name, Colors.RED, Colors.END))
        elif option == "2":
            print("{}Warning!{} Most airdrops utilize {}UTC detection to prevent cheating{}, which means they monitor your sleep patterns and the timing of your tasks. It's advisable to {}run your script when you're awake and to pause it before you go to sleep{}.".format(
                Colors.YELLOW, Colors.END, Colors.YELLOW, Colors.END, Colors.YELLOW, Colors.END
            ))
            multithread_starter()
            break
