# config.py

import os

# Unique peer ID for this device
PEER_ID = "peer_A"

# Radio configuration
RADIO_TYPE = "nrf24"  # Options: "nrf24", "lora"
RADIO_CHANNEL = 76    # nRF24 channel (0-125)
RADIO_POWER_DBM = 0   # Output power in dBm (module-dependent)
RADIO_CS_PIN = 8      # SPI Chip Select pin (GPIO for Raspberry Pi)
RADIO_IRQ_PIN = 25    # IRQ pin (GPIO for Raspberry Pi)

# Database / storage
DB_FILE = os.path.join(os.path.dirname(__file__), "data.db")

# Mesh / forwarding
MAX_TTL = 5  # Maximum hops for a message

# Flask
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000

# Map tiles
TILES_PATH = os.path.join(os.path.dirname(__file__), "tiles")

print(f"[Config] Loaded configuration. Peer ID: {PEER_ID}, Radio: {RADIO_TYPE}, DB: {DB_FILE}")
