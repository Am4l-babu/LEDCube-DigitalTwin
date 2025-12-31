#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// --- WIFI SETTINGS ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASS";
const char* pc_ip = "192.168.1.10"; // <--- CHANGE to your Laptop IP
unsigned int udpPort = 4210;

WiFiUDP Udp;

// --- HARDWARE PINS (ESP32) ---
const int dataPin = 13;   // DS (74HC595 Pin 14)
const int clockPin = 12;  // SH_CP (74HC595 Pin 11)
const int latchPin = 14;  // ST_CP (74HC595 Pin 12)
// Layer Transistors (Base pins)
const int layerPins[4] = {27, 26, 25, 33}; 

// --- CUBE MEMORY ---
// 4 integers, 16 bits each. Represents the 4x4x4 cube state.
uint16_t cube[4] = {0, 0, 0, 0}; 

// State Tracking
int currentEffect = 0; // 0=Interactive, 1=Rain, 2=Propeller, 3=Spiral

// --- HELPER FUNCTIONS ---

// 1. Clear the virtual cube
void clearCube() {
  for(int i=0; i<4; i++) cube[i] = 0;
}

// 2. Set a specific Voxel (3D Pixel)
void setVoxel(int x, int y, int z, bool state) {
  if (x<0 || x>3 || y<0 || y>3 || z<0 || z>3) return;
  
  // Map (x,y) to linear bit index (0-15)
  // Assuming standard snake wiring or row-major. Adjust if needed!
  int bitIndex = (y * 4) + x; 
  
  if (state) 
    cube[z] |= (1 << bitIndex);
  else 
    cube[z] &= ~(1 << bitIndex);
}

// 3. Send State to Python (Digital Twin)
void broadcastState() {
  Udp.beginPacket(pc_ip, udpPort);
  Udp.write('D'); // Data Header
  for(int i=0; i<4; i++) {
    Udp.write((cube[i] >> 8) & 0xFF);
    Udp.write(cube[i] & 0xFF);
  }
  Udp.endPacket();
}

// 4. THE ENGINE: Multiplexing Function
// This actually lights up the LEDs. Must be called constantly.
void render() {
  for (int z = 0; z < 4; z++) {
    // A. Turn off all layers (Ghosting prevention)
    for(int i=0; i<4; i++) digitalWrite(layerPins[i], LOW);
    
    // B. Shift out the 16 bits for this layer
    digitalWrite(latchPin, LOW);
    shiftOut(dataPin, clockPin, MSBFIRST, (cube[z] >> 8)); // High Byte
    shiftOut(dataPin, clockPin, MSBFIRST, cube[z]);        // Low Byte
    digitalWrite(latchPin, HIGH);
    
    // C. Turn on CURRENT layer
    digitalWrite(layerPins[z], HIGH);
    
    // D. Tiny delay for brightness
    delayMicroseconds(2500); 
  }
}

// 5. The Magic Wait
// Replaces delay(). Keeps cube lit while waiting.
void renderWait(int ms) {
  unsigned long start = millis();
  while (millis() - start < ms) {
    render(); // Keep drawing!
    
    // Optional: Check for UDP interrupt here to stop effects instantly
    // if(Udp.parsePacket()) break; 
  }
  broadcastState(); // Sync Twin after move
}

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  
  // Init Pins
  pinMode(dataPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  pinMode(latchPin, OUTPUT);
  for(int i=0; i<4; i++) {
    pinMode(layerPins[i], OUTPUT);
    digitalWrite(layerPins[i], LOW);
  }

  // Init WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nReady.");
  Udp.begin(udpPort);
}

// --- EFFECTS (Ported from your code) ---

void effectRain() {
  clearCube();
  int drops[16]; // Keep track of Z position for each column
  for(int i=0; i<16; i++) drops[i] = -1; // -1 means no drop
  
  for(int frames=0; frames<100; frames++) {
    // Randomly spawn drop at top (Layer 3)
    if(random(0, 5) == 0) {
      int col = random(0, 16);
      if(drops[col] == -1) drops[col] = 3; 
    }
    
    clearCube();
    for(int i=0; i<16; i++) {
      if(drops[i] >= 0) {
        // Map linear 'i' back to x,y
        setVoxel(i%4, i/4, drops[i], 1);
        drops[i]--; // Move down
      }
    }
    renderWait(100);
  }
}

void effectPropeller() {
  clearCube();
  for(int z=0; z<4; z++) { // Up
    for(int i=0; i<4; i++) { // Spin
      clearCube();
      // Draw a line based on rotation 'i'
      if(i==0) { for(int k=0; k<4; k++) setVoxel(k, 0, z, 1); } // X-axis
      if(i==1) { for(int k=0; k<4; k++) setVoxel(k, k, z, 1); } // Diagonal
      if(i==2) { for(int k=0; k<4; k++) setVoxel(0, k, z, 1); } // Y-axis
      if(i==3) { for(int k=0; k<4; k++) setVoxel(k, 3-k, z, 1); } // Diagonal 2
      renderWait(100);
    }
  }
}

void effectSpiral() {
  clearCube();
  // Simple perimeter walk
  int x=0, y=0;
  for(int i=0; i<16; i++) {
    // Logic to move x,y in a spiral is complex, simple "snake" for demo:
    setVoxel(x, y, 0, 1); // Only doing bottom layer for demo
    setVoxel(x, y, 1, 1);
    setVoxel(x, y, 2, 1);
    setVoxel(x, y, 3, 1);
    
    renderWait(100);
    x++;
    if(x>3) { x=0; y++; }
  }
}

// --- MAIN LOOP ---
void loop() {
  // 1. Check for Commands
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    char cmd[4];
    Udp.read(cmd, 4);
    
    // Command 'E' = Effect Select
    if (cmd[0] == 'E') {
      currentEffect = cmd[1];
      Serial.printf("Switched to Effect: %d\n", currentEffect);
      clearCube();
    }
    // Command 'C' = Click (Only valid in Mode 0)
    else if (cmd[0] == 'C' && currentEffect == 0) {
       int layer = cmd[1];
       int index = cmd[2];
       int state = cmd[3];
       if(state) cube[layer] |= (1 << index);
       else cube[layer] &= ~(1 << index);
    }
  }

  // 2. Run Logic
  switch(currentEffect) {
    case 0: // Interactive Mode
      render(); // Just keep drawing current state
      break;
    case 1: 
      effectRain(); 
      // After effect finishes loop, we check inputs again
      break;
    case 2: 
      effectPropeller(); 
      break;
    case 3: 
      effectSpiral(); 
      break;
    default:
      currentEffect = 0;
      break;
  }
}