import moonrakerpy as moonpy
import requests
import time

from requests.exceptions import ConnectionError
from pprint import pprint

printer = moonpy.MoonrakerPrinter('http://192.168.1.59')
addrs = "http://192.168.1.59"

url = "/server/info"

try:
    # response = requests.get(addrs + url).json()
    for _ in range(500):
        printer.send_gcode("ACCELEROMETER_QUERY")
        pprint(
            printer.get_gcode(1)
        )
        # time.sleep(0.5)

except (ConnectionError, KeyError):
    print("No query found...")
