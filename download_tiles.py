import os
import math
import requests
import time

API_KEY = "6YjT4Td7dh1qs5QoYBFL"
TILE_URL = "https://api.maptiler.com/maps/topo-v4/{z}/{x}/{y}.png?key=" + API_KEY

# Bounding box
MIN_LON, MIN_LAT = 32.439494787873, 34.93835803187357
MAX_LON, MAX_LAT = 33.52600226240776, 35.41604474498009

MIN_ZOOM = 12
MAX_ZOOM = 15

OUTPUT_DIR = "tiles"
DELAY = 0.1  # be polite

def lon_to_xtile(lon, z):
    return int((lon + 180.0) / 360.0 * (2 ** z))

def lat_to_ytile(lat, z):
    lat_rad = math.radians(lat)
    return int(
        (1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi)
        / 2.0 * (2 ** z)
    )

for z in range(MIN_ZOOM, MAX_ZOOM + 1):
    x_min = lon_to_xtile(MIN_LON, z)
    x_max = lon_to_xtile(MAX_LON, z)
    y_min = lat_to_ytile(MAX_LAT, z)
    y_max = lat_to_ytile(MIN_LAT, z)

    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            path = os.path.join(OUTPUT_DIR, str(z), str(x))
            os.makedirs(path, exist_ok=True)

            filename = os.path.join(path, f"{y}.png")
            if os.path.exists(filename):
                continue

            url = TILE_URL.format(z=z, x=x, y=y)
            print("Downloading", url)

            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
            else:
                print("Failed:", r.status_code)

            time.sleep(DELAY)
