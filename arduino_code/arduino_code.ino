#include <WiFi.h>
#include "DHT.h"

// Hardware Interface Infrastructure Pinout Mappings
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_ANALOG_PIN 34
#define LDR_ANALOG_PIN 35
#define RELAY_PUMP_PIN 25
#define SYSTEM_BUZZER_PIN 26

// Wireless Access Infrastructure Credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Cloud Metrics API Parameter Configurations
const char* CLOUD_SERVER_HOST = "api.thingspeak.com";
String CHANNEL_WRITE_TOKEN = "YOUR_THINGSPEAK_WRITE_KEY";

DHT dhtSensor(DHTPIN, DHTTYPE);
WiFiClient networkClient;

// Standard Agricultural Operational Boundary Values
const int ARID_SOIL_THRESHOLD = 1500; // Calibrated dry soil ADC crossover point [cite: 1309]

void setup() {
    Serial.begin(115200);
    
    pinMode(SOIL_ANALOG_PIN, INPUT);
    pinMode(LDR_ANALOG_PIN, INPUT);
    pinMode(RELAY_PUMP_PIN, OUTPUT);
    pinMode(SYSTEM_BUZZER_PIN, OUTPUT);
    
    // Set baseline safe hardware operational states [cite: 1295]
    digitalWrite(RELAY_PUMP_PIN, HIGH); // Deactivate relay pump loop
    digitalWrite(SYSTEM_BUZZER_PIN, LOW);
    
    dhtSensor.begin();
    establishWirelessConnection();
}

void establishWirelessConnection() {
    Serial.printf("\n[NET] Establishing wireless link to terminal: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\n[NET] Protocol authenticated. Device Node Allocated IP: %s\n", WiFi.localIP().toString().c_str());
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        establishWirelessConnection();
    }

    // Process ambient data layers from hardware channels [cite: 1300, 1301, 1302, 1303]
    float currentTemp = dhtSensor.readTemperature();
    float currentHumid = dhtSensor.readHumidity();
    int rawSoilMoisture = analogRead(SOIL_ANALOG_PIN);
    int rawAmbientLight = analogRead(LDR_ANALOG_PIN);

    if (isnan(currentTemp) || isnan(currentHumid)) {
        Serial.println("[ERROR] Broken data stream reading from DHT climate core.");
        return;
    }

    bool triggerIrrigation = false;
    String mechanicalStatus = "";

    // Closed-Loop Edge Logic Decision Processing [cite: 1308]
    if (rawSoilMoisture < ARID_SOIL_THRESHOLD) {
        // Soil water saturation limits violated -> Trigger relay irrigation [cite: 1309]
        digitalWrite(RELAY_PUMP_PIN, LOW); 
        triggerIrrigation = true;
        mechanicalStatus = "Pump_ON_Active";
    } else {
        // Soil moisture is within healthy operational envelope [cite: 1310]
        digitalWrite(RELAY_PUMP_PIN, HIGH);
        mechanicalStatus = "Pump_OFF_Standby";
    }

    // Print diagnostic logs to the local serial bus terminal [cite: 1129]
    Serial.println("=================================================");
    Serial.printf("[EDGE LOG] Temp: %.1f°C | Humid: %.1f%%\n", currentTemp, currentHumid);
    Serial.printf("[EDGE LOG] Soil Matrix ADC: %d | Light Sensor: %d\n", rawSoilMoisture, rawAmbientLight);
    Serial.printf("[EDGE LOG] Irrigation Routine State: %s\n", mechanicalStatus.c_str());

    // Stream the processed metrics out to your cloud dashboard panel [cite: 1130]
    pushTelemetryToCloud(rawSoilMoisture, currentTemp, currentHumid, rawAmbientLight, triggerIrrigation ? 1.0 : 0.0);

    // Maintain 15-second update intervals required by the free-tier ThingSpeak API
    delay(15000);
}

void pushTelemetryToCloud(int soil, float temp, float humid, int light, float pumpState) {
    if (networkClient.connect(CLOUD_SERVER_HOST, 80)) {
        String dataPayload = "api_key=" + CHANNEL_WRITE_TOKEN +
                             "&field1=" + String(soil) +
                             "&field2=" + String(temp) +
                             "&field3=" + String(humid) +
                             "&field4=" + String(light) +
                             "&field5=" + String(pumpState);

        networkClient.println("POST /update HTTP/1.1");
        networkClient.println("Host: api.thingspeak.com");
        networkClient.println("Connection: close");
        networkClient.println("Content-Type: application/x-www-form-urlencoded");
        networkClient.print("Content-Length: ");
        networkClient.println(dataPayload.length());
        networkClient.println();
        networkClient.print(dataPayload);

        Serial.println("[CLOUD] Telemetry package processed successfully by server channels.");
    } else {
        Serial.println("[CLOUD] Link failure error. Telemetry upload bypassed.");
    }
    networkClient.stop();
}