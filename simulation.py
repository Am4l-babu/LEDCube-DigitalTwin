from vpython import *
import socket
import struct
import os
from dotenv import load_dotenv

load_dotenv()
ESP_IP = os.getenv('ESP_IP', '192.168.1.15') 
UDP_PORT = int(os.getenv('UDP_PORT', 4210))

# --- Setup Scene ---
scene.title = "Digital Twin & Effect Controller"
scene.background = color.black
scene.width = 1000
scene.height = 800
scene.center = vector(3, 3, 3)

# --- Networking ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# We need to bind to listen for the "Broadcast" from ESP
sock.bind(("0.0.0.0", UDP_PORT)) 
sock.setblocking(False) # Non-blocking mode

def send_effect_command(effect_id):
    # Packet: Header 'E', Effect ID, Placeholder, Placeholder
    packet = struct.pack('BBBB', ord('E'), effect_id, 0, 0)
    sock.sendto(packet, (ESP_IP, UDP_PORT))
    print(f"Sent Effect Command: {effect_id}")

# --- Menu Handler ---
def menu_choice(m):
    val = m.selected
    if val == "Interactive (Paint)":
        send_effect_command(0)
    elif val == "Rain Effect":
        send_effect_command(1)
    elif val == "Propeller":
        send_effect_command(2)
    elif val == "Spiral":
        send_effect_command(3)

scene.append_to_caption("\nSelect Effect: ")
menu(choices=['Interactive (Paint)', 'Rain Effect', 'Propeller', 'Spiral'], bind=menu_choice)
scene.append_to_caption("\n\n")

# --- LED Grid Setup ---
leds = []
for z in range(4):     
    layer = []
    for y in range(4): 
        for x in range(4): 
            led = sphere(pos=vector(x*2, z*2, y*2), radius=0.3, color=vector(0.2,0.2,0.2))
            led.grid_pos = (x, y, z)
            layer.append(led)
    leds.append(layer)

# --- Main Loop ---
while True:
    rate(60)
    
    # 1. Listen for Updates from ESP (The Twin Logic)
    try:
        data, addr = sock.recvfrom(1024)
        if data[0] == 68: # 'D' Header
            # Parse the 4 layers (2 bytes each)
            for z in range(4):
                hi = data[1 + (z*2)]
                lo = data[1 + (z*2) + 1]
                bits = (hi << 8) | lo
                
                for i in range(16):
                    is_on = (bits >> i) & 1
                    # Map 0-15 to x,y
                    row = i // 4
                    col = i % 4
                    
                    # Update Visuals
                    target = leds[z][(row*4)+col]
                    if is_on:
                        target.color = color.cyan
                        target.emissive = True
                    else:
                        target.color = vector(0.2, 0.2, 0.2)
                        target.emissive = False
    except:
        pass # No data received this frame