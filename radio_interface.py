# radio_interface.py

import config
import time

class RadioInterface:
    """
    Abstract interface for sending/receiving messages over radio.
    Currently implemented as skeleton for nRF24L01.
    """

    def __init__(self):
        self.radio_type = config.RADIO_TYPE
        self.initialized = False
        self._initialize_radio()

    def _initialize_radio(self):
        if self.radio_type == "nrf24":
            # TODO: Integrate actual nRF24L01 library (spidev / CircuitPython)
            print("[Radio] Initializing nRF24L01...")
            self.initialized = True
        elif self.radio_type == "lora":
            # TODO: Integrate LoRa (e.g., SX1276)
            print("[Radio] LoRa initialization not implemented yet")
            self.initialized = False
        else:
            raise ValueError(f"[Radio] Unknown radio type: {self.radio_type}")
        print(f"[Radio] Initialization complete. Initialized={self.initialized}")

    def send(self, msg_bytes: bytes):
        """
        Send raw bytes over the radio.
        """
        if not self.initialized:
            raise RuntimeError("[Radio] Radio not initialized")
        print(f"[Radio] Sending {len(msg_bytes)} bytes: {msg_bytes}")

    def receive(self) -> bytes:
        """
        Non-blocking receive. Returns raw bytes if available, else None.
        """
        if not self.initialized:
            raise RuntimeError("[Radio] Radio not initialized")
        received = None  # Replace with actual data when integrated
        if received:
            print(f"[Radio] Received {len(received)} bytes")
        return received
