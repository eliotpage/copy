from flask import Flask, render_template, send_from_directory, abort, request, jsonify
import os
import math
import json

app = Flask(__name__)

TILES_DIR = "tiles"
MIN_ZOOM = 12
MAX_ZOOM = 14
DRAWINGS_FILE = "drawings.json"

# Ensure drawings file exists
if not os.path.isfile(DRAWINGS_FILE):
    with open(DRAWINGS_FILE, "w") as f:
        json.dump([], f)


# Convert tile -> lat/lng (Web Mercator)
def tile_to_latlng(x, y, z):
    n = 2 ** z
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return lat, lon


# Scan folders to find real bounds
def detect_bounds():
    z = MIN_ZOOM
    z_dir = os.path.join(TILES_DIR, str(z))

    xs = []
    ys = []

    if not os.path.isdir(z_dir):
        raise Exception("No tiles found for zoom " + str(z))

    for x in os.listdir(z_dir):
        if not x.isdigit():
            continue
        x_dir = os.path.join(z_dir, x)
        for y in os.listdir(x_dir):
            if not y.endswith(".png"):
                continue
            xs.append(int(x))
            ys.append(int(y.replace(".png", "")))

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    north, west = tile_to_latlng(min_x, min_y, z)
    south, east = tile_to_latlng(max_x + 1, max_y + 1, z)

    center_lat = (north + south) / 2
    center_lng = (west + east) / 2

    bounds = {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
        "center_lat": center_lat,
        "center_lng": center_lng
    }

    return bounds


BOUNDS = detect_bounds()


@app.route("/")
def index():
    # Load existing drawings
    with open(DRAWINGS_FILE, "r") as f:
        drawings = json.load(f)

    return render_template(
        "index.html",
        bounds=BOUNDS,
        min_zoom=MIN_ZOOM,
        max_zoom=MAX_ZOOM,
        drawings=json.dumps(drawings)
    )


@app.route("/tiles/<int:z>/<int:x>/<int:y>.png")
def serve_tile(z, x, y):
    if z < MIN_ZOOM or z > MAX_ZOOM:
        abort(404)
    max_index = (2 ** z) - 1
    if x < 0 or y < 0 or x > max_index or y > max_index:
        abort(404)

    tile_dir = os.path.join(TILES_DIR, str(z), str(x))
    tile_file = f"{y}.png"
    full_path = os.path.join(tile_dir, tile_file)

    if not os.path.isfile(full_path):
        abort(404)

    return send_from_directory(tile_dir, tile_file)


@app.route("/save_drawings", methods=["POST"])
def save_drawings():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    with open(DRAWINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
