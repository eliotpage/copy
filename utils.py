# utils.py

import uuid
import time

def generate_msg_id():
    """
    Generates a unique message ID for mesh forwarding.
    Returns a string UUID4.
    """
    msg_id = str(uuid.uuid4())
    print(f"[Utils] Generated message ID: {msg_id}")
    return msg_id

def current_timestamp():
    """
    Returns current UNIX timestamp in seconds.
    """
    ts = int(time.time())
    print(f"[Utils] Current timestamp: {ts}")
    return ts
