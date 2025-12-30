from vpython import *
import socket
import struct
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
ESP_IP = os.getenv('ESP_IP', '192.168.1.1')  # Load from .env file
UDP_PORT = int(os.getenv('UDP_PORT', '4210'))  # Load from .env file

# --- State Variables ---
# Default to RED color
current_brush_color = color.red 
brush_name = "RED"

# --- Visual Setup ---
scene.title = "Interactive Digital Twin (Color Paint Mode)"
scene.background = color.black
scene.width = 800
scene.height = 600
scene.caption = "\nControls:\n"

# --- UI Controls (Buttons) ---
def set_red(b):
    global current_brush_color, brush_name
    current_brush_color = color.red
    brush_name = "RED"
    print("Brush set to RED")

def set_green(b):
    global current_brush_color, brush_name
    current_brush_color = color.green
    brush_name = "GREEN"
    print("Brush set to GREEN")

def clear_all(b):
    # Turn off all spheres visually
    for layer in leds:
        for sphere_obj in layer:
            sphere_obj.color = color.gray(0.2)
            sphere_obj.emissive = False
    # Send "OFF" command for all layers to ESP (Optional implementation)

button(bind=set_red, text='Select RED', color=color.white, background=color.red)
scene.append_to_caption("  ") # Spacer
button(bind=set_green, text='Select GREEN', color=color.white, background=color.green)
scene.append_to_caption("  ")
button(bind=clear_all, text='Clear All', color=color.black, background=color.white)

scene.append_to_caption("\n\n")

# --- Create Grid ---
leds = []
for z in range(4):     
    layer = []
    for y in range(4): 
        for x in range(4): 
            led = sphere(pos=vector(x*2, z*2, y*2), radius=0.5, color=color.gray(0.2))
            led.grid_pos = (x, y, z) 
            led.is_on = False # Track logical state
            layer.append(led)
    leds.append(layer)

# --- Network Setup ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- Interaction Logic ---
def on_mouse_click(evt):
    hit_object = scene.mouse.pick
    
    if hit_object is not None and hasattr(hit_object, 'grid_pos'):
        x, y, z = hit_object.grid_pos
        
        # Toggle Logic
        if hit_object.is_on:
            # Turn OFF
            hit_object.color = color.gray(0.2)
            hit_object.emissive = False
            hit_object.is_on = False
            state = 0
            print(f"LED {z},{y},{x} turned OFF")
        else:
            # Turn ON with CURRENT BRUSH COLOR
            hit_object.color = current_brush_color
            hit_object.emissive = True
            hit_object.is_on = True
            state = 1
            print(f"LED {z},{y},{x} painted {brush_name}")

        # --- Hardware Communication ---
        # Since physical LEDs are single color, we just send ON (1) or OFF (0)
        # We do NOT send the color info to the ESP because the hardware doesn't support it.
        linear_index = (y * 4) + x
        packet = struct.pack('BBBB', ord('C'), z, linear_index, state)
        sock.sendto(packet, (ESP_IP, UDP_PORT))

scene.bind('mousedown', on_mouse_click)

while True:
    rate(30)