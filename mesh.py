# mesh.py

import json
import config
from storage import Storage
from utils import generate_msg_id, current_timestamp

class MeshNetwork:
    """
    Handles peer-to-peer message forwarding and deduplication.
    """

    def __init__(self, storage: Storage, radio):
        self.storage = storage
        self.radio = radio
        self.max_ttl = config.MAX_TTL
        self.neighbors = set()  # Direct neighbors
        print(f"[Mesh] Mesh initialized with max TTL={self.max_ttl}")

    def broadcast_message(self, msg_type, payload):
        msg_id = generate_msg_id()
        timestamp = current_timestamp()
        message = {
            "msg_id": msg_id,
            "origin": config.PEER_ID,
            "timestamp": timestamp,
            "type": msg_type,
            "payload": payload,
            "ttl": self.max_ttl
        }

        self.storage.add_message_seen(msg_id, timestamp)
        print(f"[Mesh] Broadcasting {msg_type} message ID {msg_id}")

        try:
            msg_bytes = json.dumps(message).encode('utf-8')
            self.radio.send(msg_bytes)
        except Exception as e:
            print(f"[Mesh] Error broadcasting message: {e}")

    def receive_message(self):
        msg_bytes = self.radio.receive()
        if not msg_bytes:
            return False

        try:
            message = json.loads(msg_bytes.decode('utf-8'))
            print(f"[Mesh] Received message: {message.get('msg_id', 'unknown')}")
        except Exception as e:
            print(f"[Mesh] Failed to decode message: {e}")
            return False

        msg_id = message.get("msg_id")
        if not msg_id:
            print("[Mesh] Message missing ID, ignoring")
            return False

        if self.storage.has_seen_message(msg_id):
            print(f"[Mesh] Already processed message ID {msg_id}")
            return False

        self.storage.add_message_seen(msg_id, message.get("timestamp"))

        self._apply_message_locally(message)

        ttl = message.get("ttl", 0)
        if ttl > 1:
            message["ttl"] = ttl - 1
            try:
                msg_bytes = json.dumps(message).encode('utf-8')
                self.radio.send(msg_bytes)
                print(f"[Mesh] Forwarded message ID {msg_id}, TTL now {message['ttl']}")
            except Exception as e:
                print(f"[Mesh] Error forwarding message: {e}")

        return True

    def _apply_message_locally(self, message):
        msg_type = message.get("type")
        payload = message.get("payload")
        origin = message.get("origin")
        timestamp = message.get("timestamp")

        if payload is None:
            print(f"[Mesh] Warning: message payload is None. Skipping")
            return

        try:
            if msg_type == "annotation":
                annotation = {
                    "id": message.get("msg_id"),
                    "peer_id": origin,
                    "timestamp": timestamp,
                    "lat": payload["lat"],
                    "lon": payload["lon"],
                    "data": payload.get("data", "")
                }
                self.storage.add_annotation(annotation)
                print(f"[Mesh] Applied annotation from {origin}")

            elif msg_type == "obstacle":
                obstacle = {
                    "id": message.get("msg_id"),
                    "peer_id": origin,
                    "timestamp": timestamp,
                    "lat": payload["lat"],
                    "lon": payload["lon"],
                    "radius": payload.get("radius", 1.0),
                    "data": payload.get("data", "")
                }
                self.storage.add_obstacle(obstacle)
                print(f"[Mesh] Applied obstacle from {origin}")
            else:
                print(f"[Mesh] Unknown message type: {msg_type}")
        except Exception as e:
            print(f"[Mesh] Error applying message locally: {e}")
