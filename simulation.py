from vpython import *
import socket
import struct
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
ESP_IP = os.getenv('ESP_IP', '192.168.1.15') 
UDP_PORT = int(os.getenv('UDP_PORT', 4210))

# --- Constants & State ---
# Layer Colors: Layer 0 (Bottom) -> Layer 3 (Top)
LAYER_COLORS = [color.blue, color.yellow, color.green, color.red]
HOVER_COLOR = vector(0.4, 0.4, 0.4) 
OFF_COLOR = vector(0.2, 0.2, 0.2)   

hovered_led = None 

# --- Visual Setup ---
scene.title = "4x4x4 Digital Twin"
scene.background = color.black
scene.width = 1000
scene.height = 800
scene.center = vector(3, 3, 3)
scene.lights = []
local_light(pos=vector(10, 10, 10), color=color.white)

# --- Networking ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_udp_command(layer, index, state):
    try:
        packet = struct.pack('BBBB', ord('C'), layer, index, state)
        sock.sendto(packet, (ESP_IP, UDP_PORT))
    except Exception as e:
        print(f"Network Error: {e}")

# --- Helper Function to Create a "Real" LED ---
def make_led(x, y, z):
    core = sphere(pos=vector(x*2, z*2, y*2), 
                  radius=0.3, 
                  color=OFF_COLOR,
                  shininess=0.8,              
                  emissive=False)
    
    glow = sphere(pos=core.pos, 
                  radius=0.8,                  
                  opacity=0.3,                 
                  visible=False,               
                  emissive=True) 
    
    core.glow_aura = glow
    core.grid_pos = (x, y, z)
    core.is_on = False
    core.my_layer_color = LAYER_COLORS[z] 
    
    return core

# --- Create Grid ---
leds_grid = [] 
leds_flat = [] 

for z in range(4):     
    layer = []
    for y in range(4): 
        for x in range(4): 
            led = make_led(x, y, z)
            layer.append(led)
            leds_flat.append(led)
    leds_grid.append(layer)

# --- Core Logic Functions ---
def set_led_state(led_obj, turn_on):
    x, y, z = led_obj.grid_pos
    
    if turn_on:
        led_obj.color = led_obj.my_layer_color + vector(0.3, 0.3, 0.3)
        led_obj.emissive = True
        led_obj.glow_aura.color = led_obj.my_layer_color
        led_obj.glow_aura.visible = True
        led_obj.is_on = True
        state_bit = 1
    else:
        led_obj.color = OFF_COLOR
        led_obj.emissive = False
        led_obj.glow_aura.visible = False
        led_obj.is_on = False
        state_bit = 0

    linear_index = (y * 4) + x
    send_udp_command(z, linear_index, state_bit)

def clear_all_synced(b):
    print("Clearing all...")
    for led_obj in leds_flat:
        if led_obj.is_on:
            set_led_state(led_obj, turn_on=False)

# --- UI Controls ---
scene.append_to_caption("\n")
button(bind=clear_all_synced, text='Clear All', color=color.black, background=color.white)

# --- Mouse Interaction Events ---
def on_mouse_click(evt):
    hit = scene.mouse.pick
    if hit is not None and hasattr(hit, 'grid_pos'):
        new_state = not hit.is_on
        set_led_state(hit, new_state)

scene.bind('mousedown', on_mouse_click)

# --- Main Animation Loop ---
while True:
    rate(60)
    
    hit_now = scene.mouse.pick

    # 1. Un-hover previous
    if hovered_led is not None and hovered_led != hit_now:
        if not hovered_led.is_on:
            hovered_led.color = OFF_COLOR
        hovered_led = None 

    # 2. Hover new
    if hit_now is not None and hasattr(hit_now, 'grid_pos'):
        if not hit_now.is_on:
             hit_now.color = HOVER_COLOR
             hovered_led = hit_now