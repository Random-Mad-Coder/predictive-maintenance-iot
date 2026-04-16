/*
 * Predictive Maintenance – Phase 1
 * Thermistor: Epcos B57164K223K (22kΩ, B~3980K)
 * Output: JSON over Serial
 */

#include <Arduino.h>

// Pins and constants
const int THERMISTOR_PIN = A0;
const float R_FIXED = 22000.0;  // 22kΩ voltage divider
const float R_NOMINAL        = 22000.0;  // Nominal resistance at 25°C
const float T_NOMINAL        = 25.0;     // °C
const float B_VALUE          = 3980.0;   // Beta value according to thermistor data sheet
const float KELVIN            = 273.15;

// Output interval in milliseconds
const unsigned long INTERVAL_MS = 30000;
unsigned long lastMeasurement = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial);  // Wait until Serial is ready
}

float readTemperature() {
  int raw = analogRead(THERMISTOR_PIN);

  // Calculate resistance of thermistor from voltage divider
  float resistance = R_FIXED * (raw / (1023.0 - raw));

  // Steinhart-Hart (simplified Beta value methode)
  float temperature = resistance / R_NOMINAL;
  temperature = log(temperature);
  temperature /= B_VALUE;
  temperature += 1.0 / (T_NOMINAL + KELVIN);
  temperature = 1.0 / temperature;
  temperature -= KELVIN;

  return temperature;
}

void loop() {
  unsigned long now = millis();

  if (now - lastMeasurement >= INTERVAL_MS) {
    lastMeasurement = now;

    float temp = readTemperature();

    // Output JSON over Serial
    Serial.print("{");
    Serial.print("\"motor_id\":");
    Serial.print("\"N20\"");
    Serial.print(",\"temperature\":");
    Serial.print(temp, 2);
    Serial.print(",\"activation_time_ms\":");
    Serial.print(now);
    Serial.println("}");
  }
}
