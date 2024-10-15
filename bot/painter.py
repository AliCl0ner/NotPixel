import random
import os
import time
from bot.utils import night_sleep, Colors, load_data_from_json, select_random_pixel
from bot.upgrades import UpgradeEnergyLimit, UpgradeReChargeSpeed, UpgradePaintReward
import config

def painters(NotPxClient, session_name):
    print("[+] {}Auto painting started{}.".format(Colors.CYAN, Colors.END))
    while True:
        try:
            user_status = NotPxClient.accountStatus()  # Ensure accountStatus is an async function
            
            if not user_status:
                time.sleep(5)  # Avoid blocking with asyncio.sleep
                continue
            
            # Accessing user_status assuming it's a dict
            charges = user_status['charges']
            balance = user_status['userBalance']
            levels_recharge = user_status['boosts']['reChargeSpeed'] + 1
            levels_paintreward = user_status['boosts']['paintReward'] + 1
            levels_energylimit = user_status['boosts']['energyLimit'] + 1

            if levels_recharge - 1 < config.RE_CHARGE_SPEED_MAX and UpgradeReChargeSpeed[levels_recharge]['Price'] <= balance:
                status = NotPxClient.upgrade_reChargeSpeed()
                print("[+] {}ReChargeSpeed Upgrade{} to level {} result: {}".format(Colors.CYAN,Colors.END,levels_recharge,status))
                balance -= UpgradeReChargeSpeed[levels_recharge]['Price']

            if levels_paintreward - 1 < config.PAINT_REWARD_MAX and UpgradePaintReward[levels_paintreward]['Price'] <= balance:
                status = NotPxClient.upgrade_paintreward()
                print("[+] {}PaintReward Upgrade{} to level {} result: {}".format(Colors.CYAN,Colors.END,levels_paintreward,status))
                balance -= UpgradePaintReward[levels_paintreward]['Price']

            if levels_energylimit - 1 < config.ENERGY_LIMIT_MAX and UpgradeEnergyLimit[levels_energylimit]['Price'] <= balance:
                status = NotPxClient.upgrade_energyLimit()
                print("[+] {}EnergyLimit Upgrade{} to level {} result: {}".format(Colors.CYAN,Colors.END,levels_energylimit,status))
                balance -= UpgradeEnergyLimit[levels_energylimit]['Price']

            if charges > 0:
                if config.X3_PIXEl:
                    data = load_data_from_json(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json')
                    for _ in range(charges):
                            color, pixelid = select_random_pixel(data)
                            pixelstatus = NotPxClient.pixelStatus(pixelid)
                            pixelcolor = pixelstatus['pixel']['color'] 
                            
                            if pixelcolor != color:
                                balance = NotPxClient.paintPixel(pixelid, color)
                                print("[+] {}{}{}: 1 {}Pixel painted{} successfully. User new balance: {}{}{}".format(
                                    Colors.CYAN, session_name, Colors.END,
                                    Colors.GREEN, Colors.END,
                                    Colors.GREEN, balance, Colors.END
                                ))
                            else:
                                print("[+] {}{}{}: {}Pixel already painted{}. Trying new pixel! User balance: {}{}{}".format(
                                    Colors.CYAN, session_name, Colors.END,
                                    Colors.RED, Colors.END,
                                    Colors.GREEN, balance, Colors.END
                                ))

                            t = random.randint(1, 10)
                            print("[!] {}{} anti-detect{}: Sleeping for {} seconds...".format(
                                Colors.CYAN, session_name, Colors.END, t
                            ))
                            time.sleep(t)  # Non-blocking sleep
                else:
                    for _ in range(charges):
                        balance = NotPxClient.autoPaintPixel()
                        print("[+] {}{}{}: 1 {}Pixel painted{} successfully. User new balance: {}{}{}".format(
                            Colors.CYAN, session_name, Colors.END,
                            Colors.GREEN, Colors.END,
                            Colors.GREEN, balance, Colors.END
                        ))

                        t = random.randint(1, 10)
                        print("[!] {}{} anti-detect{}: Sleeping for {} seconds...".format(
                            Colors.CYAN, session_name, Colors.END, t
                        ))
                        time.sleep(t)  # Non-blocking sleep
            else:
                recharge_speed = user_status['reChargeSpeed'] / 1000
                random_recharge_speed = random.randint(10, 60)
                sleep_time = round((recharge_speed + random_recharge_speed) / 60, 2)
                print("[!] {}{}{}: {}No charge available{}. Sleeping for {} minutes...".format(
                    Colors.CYAN, session_name, Colors.END,
                    Colors.YELLOW, Colors.END,
                    sleep_time
                ))
                time.sleep(recharge_speed + random_recharge_speed)  # Non-blocking sleep
        except Exception as e:
            print(f"[!] {Colors.RED}Error{Colors.END} in session {session_name}: {e}. Retrying in 5s...")
            time.sleep(5)  # Non-blocking sleep for retry
