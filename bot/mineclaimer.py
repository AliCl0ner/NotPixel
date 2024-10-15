import time
import random
from bot.utils import night_sleep, Colors

def mine_claimer(NotPxClient, session_name):
    time.sleep(5)  # Start with a delay...
    print("[+] {}Auto claiming started{}.".format(Colors.CYAN, Colors.END))
    while True:
        night_sleep()  # Check and sleep if it's between 12-1 AM Iran time
        acc_data = NotPxClient.accountStatus()
        
        if acc_data is None:
            print("[!] {}{}{}: {}Failed to retrieve account status. Retrying...{}".format(Colors.CYAN, session_name, Colors.END, Colors.RED, Colors.END))
            time.sleep(5)
            continue
        
        if 'fromStart' in acc_data and 'speedPerSecond' in acc_data:
            fromStart = acc_data['fromStart']
            speedPerSecond = acc_data['speedPerSecond']
            maxMiningTime = acc_data['maxMiningTime'] / 60
            random_recharge_speed = random.randint(30,90)

            if fromStart * speedPerSecond > 0.3:
                claimed_count = round(NotPxClient.claim_mining(), 2)
                print("[+] {}{}{}: {} NotPx Token {}Mined{}.".format(
                    Colors.CYAN, session_name, Colors.END,
                    claimed_count, Colors.GREEN, Colors.END
                ))
        else:
            print("[!] {}{}{}: {}Unexpected account data format. Retrying...{}".format(Colors.CYAN, session_name, Colors.END, Colors.RED, Colors.END))
        
        print("[!] {}{}{}: Sleeping for {} minutes...".format(Colors.CYAN, session_name, Colors.END,round((maxMiningTime+random_recharge_speed)/60),2))
        time.sleep(maxMiningTime+random_recharge_speed)
