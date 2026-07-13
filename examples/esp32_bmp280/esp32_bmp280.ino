/*
 * Nyamuk ESP32 BMP280 Template
 * 
 * ESP32 MQTT client that reads temperature, pressure, and altitude
 * from BMP280 sensor and publishes to your Nyamuk-managed Mosquitto broker.
 * 
 * Requirements:
 * - ESP32 board
 * - BMP280 sensor (I2C connection)
 * - PubSubClient library
 * - ArduinoJson library
 * - Adafruit BMP280 library
 * 
 * I2C Connections:
 * - SDA -> GPIO21
 * - SCL -> GPIO22
 * - VCC -> 3.3V
 * - GND -> GND
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

// ==================== CONFIGURATION ====================

// WiFi Settings
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Settings
const char* MQTT_SERVER = "YOUR_VPS_IP";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "esp32";
const char* MQTT_PASSWORD = "your_password";

// Device ID
const char* DEVICE_ID = "esp32_bmp280_001";

// Topic Configuration
const char* TOPIC_SENSOR = "nyamuk/esp32_bmp280_001/sensor";
const char* TOPIC_COMMAND = "nyamuk/esp32_bmp280_001/command";
const char* TOPIC_STATUS = "nyamuk/esp32_bmp280_001/status";

// Sea level pressure for altitude calculation (hPa)
const float SEA_LEVEL_PRESSURE = 1013.25;

// ==================== GLOBAL OBJECTS ====================

WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_BMP280 bmp;

unsigned long lastSensorRead = 0;
const long SENSOR_INTERVAL = 15000; // 15 seconds

// ==================== WIFI FUNCTIONS ====================

void connectWiFi() {
    Serial.print("Connecting to WiFi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
}

// ==================== MQTT FUNCTIONS ====================

void connectMQTT() {
    while (!client.connected()) {
        Serial.print("Connecting to MQTT...");
        
        String clientId = "ESP32-" + String(DEVICE_ID);
        
        if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
            Serial.println("connected!");
            client.subscribe(TOPIC_COMMAND);
            client.publish(TOPIC_STATUS, "online", true);
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds");
            delay(5000);
        }
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Message on [");
    Serial.print(topic);
    Serial.print("]: ");
    Serial.println(message);
    
    if (String(topic) == TOPIC_COMMAND) {
        if (message == "restart") {
            ESP.restart();
        } else if (message == "status") {
            publishStatus();
        } else if (message == "read") {
            publishSensorData();
        }
    }
}

// ==================== SENSOR FUNCTIONS ====================

void publishSensorData() {
    float temperature = bmp.readTemperature();
    float pressure = bmp.readPressure() / 100.0F; // Convert Pa to hPa
    float altitude = bmp.readAltitude(SEA_LEVEL_PRESSURE);
    
    StaticJsonDocument<320> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["temperature_c"] = round(temperature * 100.0) / 100.0;
    doc["pressure_hpa"] = round(pressure * 100.0) / 100.0;
    doc["altitude_m"] = round(altitude * 100.0) / 100.0;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    
    char buffer[320];
    serializeJson(doc, buffer);
    
    if (client.publish(TOPIC_SENSOR, buffer)) {
        Serial.println("BMP280 data published:");
        Serial.println(buffer);
    } else {
        Serial.println("Failed to publish sensor data");
    }
}

void publishStatus() {
    StaticJsonDocument<128> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["status"] = "online";
    doc["uptime"] = millis() / 1000;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_rssi"] = WiFi.RSSI();
    
    char buffer[128];
    serializeJson(doc, buffer);
    
    client.publish(TOPIC_STATUS, buffer, true);
}

// ==================== SETUP & LOOP ====================

void setup() {
    Serial.begin(115200);
    Serial.println("\n🦟 Nyamuk BMP280 Sensor Starting...");
    
    // Initialize I2C
    Wire.begin();
    
    // Initialize BMP280
    if (!bmp.begin(0x76)) {
        Serial.println("Could not find a valid BMP280 sensor, check wiring!");
        while (1) {
            delay(1000);
        }
    }
    
    // Configure BMP280
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,
                    Adafruit_BMP280::STANDBY_MS_500);
    
    // Connect to WiFi
    connectWiFi();
    
    // Configure MQTT
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqttCallback);
    client.setBufferSize(512);
    
    // Connect to MQTT
    connectMQTT();
    
    Serial.println("BMP280 sensor ready!");
}

void loop() {
    if (!client.connected()) {
        connectMQTT();
    }
    client.loop();
    
    unsigned long now = millis();
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
        lastSensorRead = now;
        publishSensorData();
    }
    
    delay(10);
}
