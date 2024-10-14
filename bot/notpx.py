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

    async def init_async(self):
        await self.__update_headers()

    async def __update_headers(self):
        async with TelegramClient(self.session_name, config.API_ID, config.API_HASH) as client:
            WebAppQuery = await self.GetWebAppData(client)

        self.session.headers = {
            'Authorization': f'initData {WebAppQuery}',
        }

    async def GetWebAppData(self, client):
        notcoin = await client.get_entity("notpixel")
        msg = await client(functions.messages.RequestWebViewRequest(notcoin, notcoin, platform="android", url="https://notpx.app/"))
        webappdata_global = msg.url.split('https://notpx.app/#tgWebAppData=')[1].replace("%3D", "=").split('&tgWebAppVersion=')[0].replace("%26", "&")
        user_data = webappdata_global.split("&user=")[1].split("&auth")[0]
        webappdata_global = webappdata_global.replace(user_data, unquote(user_data))
        return webappdata_global

    async def request(self, method, end_point, key_check, data=None):
        try:
            if method == "get":
                response = self.session.get(f"https://notpx.app/api/v1{end_point}", timeout=15)
            else:
                response = self.session.post(f"https://notpx.app/api/v1{end_point}", timeout=15, json=data)

            # Handle NotPixel heavy load error
            if "failed to parse" in response.text:
                print("[x] {}NotPixel internal error. Wait 5 minutes...{}".format(Colors.RED, Colors.END))
                await asyncio.sleep(5 * 60)  # Use asyncio.sleep instead of time.sleep
            elif response.status_code == 200:
                # print(response.json())
                if key_check in response.text:
                    return response.json() # Return the JSON response
                else:
                    raise Exception(report_bug_text.format(response.text))
            elif response.status_code >= 500:
                await asyncio.sleep(5)  # Use asyncio.sleep for non-blocking sleep
            else:
                # Renew authentication within the existing event loop
                try:
                    async with TelegramClient(self.session_name, config.API_ID, config.API_HASH) as client:
                        WebAppQuery = await self.GetWebAppData(client)

                    # Update headers with the renewed authentication
                    self.session.headers.update({
                        "Authorization": "initData " + WebAppQuery
                    })
                    print("[+] Authentication renewed!")
                    await asyncio.sleep(2)  # Use 'asyncio.sleep' for non-blocking sleep
                except Exception as e:
                    print(f"[-] Error during authentication renewal: {e}")

        except (requests.exceptions.ConnectionError, 
                urllib3.exceptions.NewConnectionError, 
                requests.exceptions.Timeout) as e:
            print(f"[!] {Colors.RED}{type(e).__name__}{Colors.END} {end_point}. Sleeping for 5s...")
            await asyncio.sleep(5)

    async def claim_mining(self):
        response = await self.request("get", "/mining/claim", "claimed")  # Await the request
        return response['claimed']  # Access the result after awaiting

    async def accountStatus(self):
        response = await self.request("get", "/mining/status", "speedPerSecond")
        return response

    async def pixelStatus(self, pixelid):
        response = await self.request("get", f"/image/get/{pixelid}", "isAvailable")
        return response

    async def autoPaintPixel(self):
        colors = ["#FFFFFF", "#000000", "#00CC78", "#BE0039"]
        random_pixel = (random.randint(100, 990) * 1000) + random.randint(100, 990)
        data = {"pixelId": random_pixel, "newColor": random.choice(colors)}

        response = await self.request("post", "/repaint/start", "balance", data)
        return response['balance']

    async def paintPixel(self, pixelformated, hex_color):
        data = {"pixelId": pixelformated, "newColor": hex_color}
        response = await self.request("post", "/repaint/start", "balance", data)
        return response['balance']

    async def upgrade_paintreward(self):
        response = await self.request("get", "/mining/boost/check/paintReward", "paintReward")
        return response['paintReward']

    async def upgrade_energyLimit(self):
        response = await self.request("get", "/mining/boost/check/energyLimit", "energyLimit")
        return response['energyLimit']

    async def upgrade_reChargeSpeed(self):
        response = await self.request("get", "/mining/boost/check/reChargeSpeed", "reChargeSpeed")
        return response['reChargeSpeed']
