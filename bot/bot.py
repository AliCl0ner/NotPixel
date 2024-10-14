import os
import threading
import asyncio
from bot.painter import painters
from bot.mineclaimer import mine_claimer
from bot.utils import night_sleep, Colors
from bot.notpx import NotPx
import config
from telethon.sync import TelegramClient

async def run_sessions(session_name):
    cli = NotPx("sessions/" + session_name)
    await cli.init_async()
    # Run painters and mine_claimer concurrently
    await asyncio.gather(
        painters(cli, session_name),
        mine_claimer(cli, session_name)
    )

async def start_all_sessions():
    dirs = os.listdir("sessions/")
    sessions = list(filter(lambda x: x.endswith(".session"), dirs))
    sessions = list(map(lambda x: x.split(".session")[0], sessions))

    tasks = []
    for session_name in sessions:
        try:
            tasks.append(run_sessions(session_name))
        except Exception as e:
            print("[!] {}Error on load session{} \"{}\", error: {}".format(Colors.RED, Colors.END, session_name, e))

    # Wait for all sessions to complete
    await asyncio.gather(*tasks)

def multithread_starter():
    # Function to run the event loop inside the thread
    def run_event_loop():
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # Set it as the current event loop
        
        try:
            loop.run_until_complete(start_all_sessions())  # Run the event loop
        finally:
            loop.close()  # Close the loop when done

    # Create a new thread to run the event loop
    loop_thread = threading.Thread(target=run_event_loop)
    loop_thread.start()
    return loop_thread  # Return the thread to optionally join later

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
            loop_thread = multithread_starter()  # Start the multithreaded session
            loop_thread.join()  # Wait for the thread to complete
            break
