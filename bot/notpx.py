import requests
from urllib.parse import unquote
import config
import time
import asyncio
from telethon.sync import TelegramClient, functions
import urllib3
from bot.utils import Colors
import random
report_bug_text = "If you have done all the steps correctly and you think this is a bug, report it to github.com/ALICL0ner with response. response: {}"
class NotPx:
    def __init__(self, session_name:str) -> None:
        self.session = requests.Session()
        if config.USE_PROXY:
            self.session.proxies = {
                    "http": config.PROXIES,
                    "https": config.PROXIES, 
                }
            try:
                if "http" not in self.session.proxies or "https" not in self.session.proxies:
                    raise ValueError(f"{Colors.RED}[ERROR]{Colors.END} Both 'http' and 'https' proxies must be defined.")
                print(f"Using proxy: {self.session.proxies}")
                response = requests.get('https://app.notpx.app/', proxies=self.session.proxies)
                print(response.raise_for_status())
                print("{}Proxy is working correctly.{}".format(Colors.GREEN, Colors.END))
            except requests.exceptions.ProxyError as e:
                print("{}Proxy failed:{} {}".format(Colors.RED, Colors.END,e))
                raise SystemExit("{}[ERROR]{} Proxy is not working. Exiting...".format(Colors.RED, Colors.END))
            except requests.exceptions.ConnectionError as e:
                print("{}Connection error:{} {}".format(Colors.RED, Colors.END,e))
                raise SystemExit("{}[ERROR]{} Connection error. Exiting...".format(Colors.RED, Colors.END))
            except requests.exceptions.Exception as e:
                print("{}An unexpected error occurred:{} {}".format(Colors.RED, Colors.END,e))
                raise SystemExit("{}[ERROR]{} Unexpected error. Exiting...".format(Colors.RED, Colors.END))
        self.session_name = session_name
        self.__update_headers()

    def __update_headers(self):
        client = TelegramClient(self.session_name, config.API_ID, config.API_HASH).start()
        WebAppQuery = client.loop.run_until_complete(self.GetWebAppData(client))
        client.disconnect()
        self.session.headers = {
            'Authorization': f'initData {WebAppQuery}',
        }

    async def GetWebAppData(self, client):
        notcoin = await client.get_entity("notpixel")
        msg = await client(functions.messages.RequestWebViewRequest(notcoin,notcoin,platform="android",url="https://notpx.app/"))
        webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D","=").split('&tgWebAppVersion=')[0].replace("%26","&")
        user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
        webappdata_global = webappdata_global.replace(user_data, unquote(user_data))
        return webappdata_global

    def request(self, method, end_point, key_check, data=None, retries=3):
        try:
            if method == "get":
                response = self.session.get(f"https://notpx.app/api/v1{end_point}", timeout=5)
            else:
                response = self.session.post(f"https://notpx.app/api/v1{end_point}", timeout=5, json=data)

            # Handle NotPixel heavy load error
            if "failed to parse" in response.text:
                print("[x] {}NotPixel internal error. Wait 5 minutes...{}".format(Colors.RED, Colors.END))
                time.sleep(5 * 60)
            elif response.status_code == 200:
                if key_check in response.text:
                    return response.json()  # Return the JSON response
                else:
                    raise Exception(report_bug_text.format(response.text))
            elif response.status_code >= 500:
                time.sleep(5)  # Sleep for 5 seconds on server errors
            else:
                # Create a new event loop, renew authentication, and close the loop afterward
                nloop = asyncio.new_event_loop()
                asyncio.set_event_loop(nloop)
                try:
                    client = TelegramClient(self.session_name, config.API_ID, config.API_HASH, loop=nloop).start()
                    WebAppQuery = nloop.run_until_complete(self.GetWebAppData(client))
                    client.disconnect()
                    self.session.headers.update({
                        "Authorization": "initData " + WebAppQuery
                    })
                    print("[+] Authentication renewed!")
                    time.sleep(2)
                finally:
                    nloop.close()  # Ensure the event loop is closed

        except (requests.exceptions.ConnectionError, 
                urllib3.exceptions.NewConnectionError, 
                requests.exceptions.Timeout) as e:
            print(f"[!] {Colors.RED}{type(e).__name__}{Colors.END} {end_point}. Sleeping for 5s...")
            time.sleep(5)
            
        # Retry logic with a retry limit
        if retries > 0:
            return self.request(method, end_point, key_check, data, retries - 1)
        else:
            raise Exception(f"Max retries reached for {end_point}")

    def claim_mining(self):
        return self.request("get","/mining/claim","claimed")['claimed']

    def accountStatus(self):
        return self.request("get","/mining/status","speedPerSecond")
    
    def pixelStatus(self,pixelid):
        return self.request("get",f"/image/get/{pixelid}","isAvailable")
    
    def autoPaintPixel(self):
        # making pixel randomly
        colors = [ "#FFFFFF" , "#000000" , "#00CC78" , "#BE0039" ]
        random_pixel = (random.randint(100,990) * 1000) + random.randint(100,990)
        data = {"pixelId":random_pixel,"newColor":random.choice(colors)}

        return self.request("post","/repaint/start","balance",data)['balance']
    
    def paintPixel(self,pixelformated,hex_color):
        # pixelformated = (y * 1000) + x + 1
        data = {"pixelId":pixelformated,"newColor":hex_color}

        return self.request("post","/repaint/start","balance",data)['balance']
    
    def upgrade_paintreward(self):
        return self.request("get","/mining/boost/check/paintReward","paintReward")['paintReward']
    
    def upgrade_energyLimit(self):
        return self.request("get","/mining/boost/check/energyLimit","energyLimit")['energyLimit']
    
    def upgrade_reChargeSpeed(self):
        return self.request("get","/mining/boost/check/reChargeSpeed","reChargeSpeed")['reChargeSpeed']
