volatile int pulseCount = 0;
float flowRate = 0.0;
unsigned long lastTime = 0;

#define FLOW_SENSOR_PIN 4

void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), pulseCounter, RISING);

  lastTime = millis();
}

void loop() {
  if (millis() - lastTime >= 1000) { // toutes les 1 seconde
    
    noInterrupts(); // stop interruptions temporairement
    int pulses = pulseCount;
    pulseCount = 0;
    interrupts(); // reprendre interruptions

    // Calcul du débit (L/min)
    flowRate = pulses / 7.5;

    Serial.print("Pulses: ");
    Serial.print(pulses);
    Serial.print(" | Débit: ");
    Serial.print(flowRate);
    Serial.println(" L/min");

    lastTime = millis();
  }
}