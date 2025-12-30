#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "arduino_secrets.h" // Contains WiFi credentials and IP details  

// --- WIFI CONFIG ---
const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS; 
const char* pc_ip = SECRET_PC_IP; // Defined in arduino_secrets.h
unsigned int udpPort = 4210; // Listening port

WiFiUDP Udp;

// Define your 16 Pins for Layer 0
const int layer0Pins[] = {13, 12, 14, 27, 26, 25, 33, 32, 15, 23, 4, 5, 18, 19, 21, 22};

void setup() {
  Serial.begin(115200);
  
  // 1. Setup Pins
  for (int i = 0; i < 16; i++) {
    pinMode(layer0Pins[i], OUTPUT);
    digitalWrite(layer0Pins[i], LOW);
  }

  // 2. Connect WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");
  Serial.print("ESP IP Address: ");
  Serial.println(WiFi.localIP()); // <--- COPY THIS IP to your .env file

  // 3. Start Listening
  Udp.begin(udpPort);
  Serial.printf("UDP Listening on port %d\n", udpPort); // <--- PRINT "LISTENING"
}

void loop() {
  // Check for incoming packets
  int packetSize = Udp.parsePacket();
  
  if (packetSize) {
    // We received data!
    Serial.printf("Received packet of size %d from %s\n", packetSize, Udp.remoteIP().toString().c_str());

    char packetBuffer[4];
    Udp.read(packetBuffer, 4);

    // If it's a Command 'C'
    if (packetBuffer[0] == 'C') {
       // packetBuffer[1] is Layer (ignore for now if only testing layer 0)
       int ledIndex = packetBuffer[2];
       int state = packetBuffer[3];
       
       Serial.printf("Command: LED %d -> %s\n", ledIndex, state ? "ON" : "OFF");

       if (ledIndex >= 0 && ledIndex < 16) {
          digitalWrite(layer0Pins[ledIndex], state ? HIGH : LOW);
       }
    }
  }
}