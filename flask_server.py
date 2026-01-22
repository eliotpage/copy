# flask_server.py

from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import time
import os

from storage import Storage
from mesh import MeshNetwork
from radio_interface import RadioInterface
from routing import DStarLite
import config

app = Flask(__name__)
storage = Storage()
radio = RadioInterface()
mesh = MeshNetwork(storage, radio)
routing = DStarLite(storage, width=100, height=100, default_cost=1)

print("[Server] Flask server initialized")

@app.route('/tiles/<path:filename>')
def serve_tiles(filename):
    tiles_dir = config.TILES_PATH
    file_path = os.path.join(tiles_dir, filename)
    if not os.path.exists(file_path):
        print(f"[Server] Tile not found: {filename}")
    else:
        print(f"[Server] Serving tile: {filename}")
    return send_from_directory(tiles_dir, filename)

@app.route('/')
def index():
    print("[Server] Serving index page")
    return render_template('index.html')

@app.route('/api/add_annotation', methods=['POST'])
def add_annotation():
    data = request.json
    if not data or 'lat' not in data or 'lon' not in data:
        print("[Server] add_annotation missing lat/lon")
        return jsonify({'status': 'error', 'message': 'Missing lat/lon'}), 400

    annotation = {
        'lat': data['lat'],
        'lon': data['lon'],
        'data': data.get('data', '')
    }

    mesh.broadcast_message("annotation", annotation)
    print(f"[Server] Annotation broadcasted: {annotation}")

    return jsonify({'status': 'ok'})

@app.route('/api/add_obstacle', methods=['POST'])
def add_obstacle():
    data = request.json
    if not data or 'lat' not in data or 'lon' not in data or 'radius' not in data:
        print("[Server] add_obstacle missing lat/lon/radius")
        return jsonify({'status': 'error', 'message': 'Missing lat/lon/radius'}), 400

    obstacle = {
        'lat': data['lat'],
        'lon': data['lon'],
        'radius': data['radius'],
        'data': data.get('data', '')
    }

    mesh.broadcast_message("obstacle", obstacle)
    print(f"[Server] Obstacle broadcasted: {obstacle}")

    return jsonify({'status': 'ok'})

@app.route('/api/get_annotations', methods=['GET'])
def get_annotations():
    annotations = storage.get_all_annotations()
    print(f"[Server] Returning {len(annotations)} annotations")
    return jsonify(annotations)

@app.route('/api/get_obstacles', methods=['GET'])
def get_obstacles():
    obstacles = storage.get_all_obstacles()
    print(f"[Server] Returning {len(obstacles)} obstacles")
    return jsonify(obstacles)

@app.route('/api/get_path', methods=['POST'])
def get_path():
    data = request.json
    if not data or 'start' not in data or 'goal' not in data:
        print("[Server] get_path missing start/goal")
        return jsonify({'status': 'error', 'message': 'Missing start/goal'}), 400

    start = data['start']
    goal = data['goal']

    try:
        path = routing.find_path(start, goal)
    except Exception as e:
        print(f"[Server] Error finding path: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    path_latlon = [routing_grid_to_latlon(xy) for xy in path]
    print(f"[Server] Path returned with {len(path_latlon)} points")

    return jsonify({'status': 'ok', 'path': path_latlon})

def routing_grid_to_latlon(grid_coord):
    x, y = grid_coord
    lat = x * (180 / routing.width)
    lon = y * (360 / routing.height)
    return [lat, lon]

def mesh_listener():
    print("[Server] Mesh listener thread started")
    while True:
        try:
            mesh.receive_message()
        except Exception as e:
            print(f"[Server] Error in mesh_listener: {e}")
        time.sleep(0.01)

listener_thread = threading.Thread(target=mesh_listener, daemon=True)
listener_thread.start()

if __name__ == '__main__':
    if not os.path.exists(config.TILES_PATH):
        os.makedirs(config.TILES_PATH)
        print(f"[Server] Created tiles folder: {config.TILES_PATH}")

    print(f"[Server] Starting Flask on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, threaded=True)
