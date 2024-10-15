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
    def __init__(self, session_name: str) -> None:
        self.session = requests.Session()

        # Proxy setup
        if config.USE_PROXY:
            self.session.proxies = {
                "http": config.PROXIE,
                "https": config.PROXIE,
            }
            try:
                if "http" not in self.session.proxies or "https" not in self.session.proxies:
                    raise ValueError(f"{Colors.RED}[ERROR]{Colors.END} Both 'http' and 'https' proxies must be defined.")
                print(f"Using proxy: {self.session.proxies}")
                response = requests.get('https://app.notpx.app/', proxies=self.session.proxies)
                response.raise_for_status()
                print(f"{Colors.GREEN}Proxy is working correctly.{Colors.END}")
            except requests.exceptions.ProxyError as e:
                print(f"{Colors.RED}Proxy failed:{Colors.END} {e}")
                raise SystemExit(f"{Colors.RED}[ERROR]{Colors.END} Proxy is not working. Exiting...")
            except requests.exceptions.ConnectionError as e:
                print(f"{Colors.RED}Connection error:{Colors.END} {e}")
                raise SystemExit(f"{Colors.RED}[ERROR]{Colors.END} Connection error. Exiting...")
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}An unexpected error occurred:{Colors.END} {e}")
                raise SystemExit(f"{Colors.RED}[ERROR]{Colors.END} Unexpected error. Exiting...")

        self.session_name = session_name
        self.__update_headers()
        
    def __update_headers(self):
        client = TelegramClient(self.session_name,config.API_ID,config.API_HASH).start()
        WebAppQuery = client.loop.run_until_complete(self.GetWebAppData(client))
        client.disconnect()
        self.session.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': f'initData {WebAppQuery}',
            'Priority': 'u=1, i',
            'Referer': 'https://notpx.app/',
            'Sec-Ch-Ua': 'Chromium;v=119, Not?A_Brand;v=24',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': 'Linux',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.105 Safari/537.36',
        }

    async def GetWebAppData(self, client):
        notcoin = await client.get_entity("notpixel")
        msg = await client(functions.messages.RequestWebViewRequest(notcoin, notcoin, platform="android", url="https://notpx.app/"))
        webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D", "=").split('&tgWebAppVersion=')[0].replace("%26", "&")
        user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
        webappdata_global = webappdata_global.replace(user_data, unquote(user_data))
        return webappdata_global

    def request(self, method, end_point, key_check, data=None):
        try:
            if method == "get":
                response = self.session.get(f"https://notpx.app/api/v1{end_point}", timeout=15)
            else:
                response = self.session.post(f"https://notpx.app/api/v1{end_point}", timeout=15, json=data)

            # Handle NotPixel heavy load error
            if "failed to parse" in response.text:
                print("[x] {}NotPixel internal error. Wait 5 minutes...{}".format(Colors.RED, Colors.END))
                time.sleep(5 * 60)
            elif response.status_code == 200:
                # print(response.json())
                if key_check in response.text:
                    return response.json() # Return the JSON response
                else:
                    raise Exception(report_bug_text.format(response.text))
            elif response.status_code >= 500:
                time.sleep(5)
            else:
                # Renew authentication within the existing event loop
                try:
                    with TelegramClient(self.session_name, config.API_ID, config.API_HASH) as client:
                        WebAppQuery = self.GetWebAppData(client)

                    # Update headers with the renewed authentication
                    self.session.headers.update({
                        "Authorization": "initData " + WebAppQuery
                    })
                    print("[+] Authentication renewed!")
                    time.sleep(2) 
                except Exception as e:
                    print(f"[-] Error during authentication renewal: {e}")

        except (requests.exceptions.ConnectionError, 
                urllib3.exceptions.NewConnectionError, 
                requests.exceptions.Timeout) as e:
            print(f"[!] {Colors.RED}{type(e).__name__}{Colors.END} {end_point}. Sleeping for 5s...")
            time.sleep(5)
        return self.request(method, end_point, key_check, data)
        
    def claim_mining(self):
        return self.request("get", "/mining/claim", "claimed")['claimed'] 

    def accountStatus(self):
        return self.request("get", "/mining/status", "speedPerSecond")
        

    def pixelStatus(self, pixelid):
        return self.request("get", f"/image/get/{pixelid}", "isAvailable")

    def autoPaintPixel(self):
        colors = ["#FFFFFF", "#000000", "#00CC78", "#BE0039"]
        random_pixel = (random.randint(100, 990) * 1000) + random.randint(100, 990)
        data = {"pixelId": random_pixel, "newColor": random.choice(colors)}

        return self.request("post", "/repaint/start", "balance", data)['balance']

    def paintPixel(self, pixelformated, hex_color):
        data = {"pixelId": pixelformated, "newColor": hex_color}
        response = self.request("post", "/repaint/start", "balance", data)
        return response['balance']

    def upgrade_paintreward(self):
        return self.request("get", "/mining/boost/check/paintReward", "paintReward")['paintReward']

    def upgrade_energyLimit(self):
        return self.request("get", "/mining/boost/check/energyLimit", "energyLimit")['energyLimit']

    def upgrade_reChargeSpeed(self):
        return self.request("get", "/mining/boost/check/reChargeSpeed", "reChargeSpeed")['reChargeSpeed']
