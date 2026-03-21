#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "MIMI";
const char* password = "Raz23Mim";
const char* serverUrl = "http://192.168.88.119:5000/api/measurements";
const char* sensorId = "FLOW001";

#define FLOW_PIN     21
#define CONTROL_PIN  19

// FlowSensor
volatile int pulseCount = 0;
float flowRate = 0;
unsigned long lastCalc = 0;
const float calibrationFactor = 4.5;

bool pompeOn = true;

// INTERRUPTION
void IRAM_ATTR countPulse() {
  pulseCount++;
}

// Flow rate calculation
void updateFlow() {
  unsigned long now = millis();
  if (now - lastCalc >= 1000) {
    flowRate = (pulseCount / calibrationFactor) * 60;
    pulseCount = 0;
    lastCalc = now;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=== ESP32 DEMARRAGE ===\n");
  
  // 1. Configuration
  Serial.println("Configuration du debitmetre...");
  pinMode(FLOW_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), countPulse, RISING);
  
  // 2. WiFi Connection (with timeout)
  Serial.print("Connexion au WiFi ");
  Serial.print(ssid);
  Serial.print("...");
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connecte !");
    Serial.print("   IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Signal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("Echec connexion WiFi !");
    Serial.print("   Statut: ");
    switch(WiFi.status()) {
      case WL_NO_SSID_AVAIL:
        Serial.println("Reseau non trouve");
        break;
      case WL_CONNECT_FAILED:
        Serial.println("Mot de passe incorrect");
        break;
      default:
        Serial.println(WiFi.status());
    }
  }
}

void loop() {
  updateFlow();
  
  // Printing every 2 seconds
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint >= 2000) {
    Serial.print("Debit: ");
    Serial.print(flowRate);
    Serial.print(" L/min | WiFi: ");
    Serial.print(WiFi.status() == WL_CONNECTED ? "OK" : "KO");
    Serial.println();
    lastPrint = millis();
  }
  
  // Sendind data
  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 10000) {
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      
      String json = "{\"sensor_id\":\"" + String(sensorId) +
                    "\",\"value\":" + String(flowRate) +
                    ",\"pump_on\":" + String(pompeOn ? "true" : "false") + "}";
      
      Serial.print("Envoi: ");
      Serial.print(json);
      
      int code = http.POST(json);
      Serial.print("Reponse: ");
      Serial.println(code);
      
      http.end();
    } else {
      Serial.println("WiFi deconnecte");
    }
    lastSend = millis();
  }
  
  delay(50);
}