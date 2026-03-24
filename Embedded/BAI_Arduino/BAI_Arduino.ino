#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "iPhone";
const char* password = "idealyryan";
const char* serverUrl = "http://172.20.10.2:5000/api/measurements";
const char* sensorId = "FLOW001";

#define FLOW_PIN     21
#define RELAY_PIN    19
#define BUTTON_PIN   18

//PARAMÈTRES DE CORRECTION
const float CALIBRATION = 4.5;      // impulsions par litre
const float DIVISOR = 11000;        // Diviseur pour corriger

//VARIABLES
volatile int pulseCount = 0;
float flowRate = 0;
unsigned long lastTime = 0;
unsigned long lastSend = 0;
bool pumpState = false;
bool lastButton = HIGH;

//INTERRUPTION
void IRAM_ATTR countPulse() {
  pulseCount++;
}

// CALCUL DEBIT AVEC DIVISION
void calcFlow() {
  if (millis() - lastTime >= 1000) {
    noInterrupts();
    int pulses = pulseCount;
    pulseCount = 0;
    interrupts();
    
    // Calcul brut
    float rawFlow = (pulses / CALIBRATION) * 60;
    
    // Application de la division
    flowRate = rawFlow / DIVISOR;
    
    // Éviter les valeurs négatives
    if (flowRate < 0) flowRate = 0;
    
    // Afficher les valeurs brutes si parasites (optionnel)
    if (rawFlow > 1000) {
      Serial.print("Brut: ");
      Serial.print(rawFlow);
      Serial.print("Corrigé: ");
      Serial.println(flowRate);
    }
    
    lastTime = millis();
  }
}

// POMPE
void setPump(bool on) {
  pumpState = on;
  digitalWrite(RELAY_PIN, pumpState ? HIGH : LOW);
  
  // Remise à zéro du compteur après changement d'état
  noInterrupts();
  pulseCount = 0;
  interrupts();
  
  Serial.print("Pompe: ");
  Serial.println(pumpState ? "ON" : "OFF");
}

// BOUTON
void checkButton() {
  bool btn = digitalRead(BUTTON_PIN);
  if (btn == LOW && lastButton == HIGH) {
    setPump(!pumpState);
    delay(300);
  }
  lastButton = btn;
}

// WIFI
void connectWiFi() {
  Serial.println("\nTEST CONNEXION WIFI\n");
  Serial.print("SSID: ");
  Serial.println(ssid);
  Serial.print("Mot de passe: ");
  Serial.println(password);
  Serial.println();
  
  Serial.print("Connexion");
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  
  Serial.println();
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nCONNEXION REUSSIE !\n");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("Diviseur: ");
    Serial.println(DIVISOR);
  } else {
    Serial.println("\nCONNEXION ECHOUEE\n");
    Serial.print("Statut: ");
    switch(WiFi.status()) {
      case WL_NO_SSID_AVAIL:
        Serial.println("Réseau non trouvé");
        break;
      case WL_CONNECT_FAILED:
        Serial.println("Mot de passe incorrect");
        break;
      default:
        Serial.println(WiFi.status());
    }
  }
}

// ENVOI SERVEUR
void sendData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi déconnecté, envoi impossible");
    return;
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  String json = "{\"sensor_id\":\"" + String(sensorId) +
                "\",\"value\":" + String(flowRate) +
                ",\"pump_on\":" + String(pumpState ? "true" : "false") + "}";
  
  Serial.print("Envoi: ");
  Serial.println(json);
  
  int code = http.POST(json);
  Serial.print("Réponse: ");
  
  if (code == 200 || code == 201) {
    Serial.println("OK");
  } else {
    Serial.print("Erreur ");
    Serial.println(code);
  }
  
  http.end();
}

// SETUP
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\nBLUEAI START\n");
  Serial.print("Diviseur de correction: ");
  Serial.println(DIVISOR);
  Serial.println("   (22000 brut = 2 L/min)");
  Serial.println();
  
  // Configuration broches
  pinMode(FLOW_PIN, INPUT_PULLUP);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  digitalWrite(RELAY_PIN, LOW);
  pumpState = false;
  
  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), countPulse, RISING);
  
  Serial.println("Capteur débit OK");
  Serial.println("Relais OK");
  Serial.println("Bouton OK");
  
  connectWiFi();
  
  Serial.println("\nCOMMANDES:");
  Serial.println("   • Bouton : appui = inverse pompe");
  Serial.println("   • Série : 1=ON, 0=OFF");
  Serial.println("   • Envoi serveur toutes les 10s");
  Serial.print("   • Diviseur = ");
  Serial.println(DIVISOR);
  Serial.println("   • Débit = (impulsions/4.5)*60 / DIVISEUR\n");
}

// LOOP
void loop() {
  // Bouton
  checkButton();
  
  // Commande série
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '1') setPump(true);
    if (c == '0') setPump(false);
  }
  
  // Calcul débit
  calcFlow();
  
  // Affichage (toutes les 2s)
  static unsigned long lastShow = 0;
  if (millis() - lastShow >= 2000) {
    Serial.print("Débit: ");
    Serial.print(flowRate);
    Serial.print(" L/min | Pompe: ");
    Serial.print(pumpState ? "ON" : "OFF");
    Serial.print(" | WiFi: ");
    Serial.println(WiFi.status() == WL_CONNECTED ? "OK" : "NO");
    lastShow = millis();
  }
  
  // Envoi serveur (toutes les 10s)
  if (millis() - lastSend >= 10000) {
    sendData();
    lastSend = millis();
  }
  
  delay(50);
}