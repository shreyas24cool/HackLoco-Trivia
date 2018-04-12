import asyncio
import logging
import time
from datetime import datetime

import networking

# Set up logging
logging.basicConfig(filename="data.log", level=logging.INFO, filemode="w")

# Read in bearer token and user ID
with open("conn_settings.txt", "r") as conn_settings:
    BEARER_TOKEN = conn_settings.readline().strip().split("=")[1]
    DEVICE_ID = conn_settings.readline().strip().split("=")[1]

print("getting")
main_url = f"https://api.getloconow.com/v1/contests/"
headers = {"User-Agent": "Ql7xwaHIItRhjySAjrCX6JmwsKXjL",
           "X-APP-VERSION": "60",
           "X-PLATFORM": "1",
           "Device-Id": DEVICE_ID,
           "Authorization": f"Bearer {BEARER_TOKEN}",
           "Host": "api.getloconow.com",
           "Connection": "Keep-Alive",
           "Accept-Encoding": "gzip"}

while True:
    print()
    try:
        response_data = asyncio.get_event_loop().run_until_complete(
            networking.get_json_response(main_url, timeout=1.5, headers=headers))
    except:
        print("Server response not JSON, retrying...")
        time.sleep(1)
        continue

    logging.info(response_data)

    if "broadcast" not in response_data or response_data["broadcast"] is None:
        if "detail" in response_data and response_data["detail"] == "Authentication credentials were not provided.":
            raise RuntimeError("Connection settings invalid")
        else:
            print("Show not on.")
            show_time = datetime.fromtimestamp(int(response_data["show_time"])/1000)

            print(f"Next show time: {show_time.strftime('%Y-%m-%d %I:%M %p')}")
            time.sleep(5)
    else:
        socket = response_data["broadcast"]["socketUrl"]
        print(f"Show active, connecting to socket at {socket}")
        asyncio.get_event_loop().run_until_complete(networking.websocket_handler(socket, headers))
