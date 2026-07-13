/*
 * Nyamuk ESP32 Basic Template
 * 
 * This is a basic ESP32 MQTT client that connects to your Mosquitto broker
 * managed by Nyamuk. It publishes generic JSON sensor data.
 * 
 * Requirements:
 * - ESP32 board
 * - PubSubClient library
 * - ArduinoJson library
 * 
 * Configuration:
 * - Update WiFi credentials
 * - Update MQTT broker IP/hostname
 * - Update MQTT credentials
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================

// WiFi Settings
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Settings
const char* MQTT_SERVER = "YOUR_VPS_IP";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "esp32";
const char* MQTT_PASSWORD = "your_password";

// Device ID (unique per ESP32)
const char* DEVICE_ID = "esp32_001";

// Topic Configuration
const char* TOPIC_PREFIX = "nyamuk";
const char* TOPIC_SENSOR = "nyamuk/esp32_001/sensor";
const char* TOPIC_COMMAND = "nyamuk/esp32_001/command";
const char* TOPIC_STATUS = "nyamuk/esp32_001/status";

// ==================== GLOBAL OBJECTS ====================

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastSensorRead = 0;
const long SENSOR_INTERVAL = 5000; // 5 seconds

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
            
            // Subscribe to command topic
            client.subscribe(TOPIC_COMMAND);
            
            // Publish online status
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
    // Convert payload to string
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Message received on [");
    Serial.print(topic);
    Serial.print("]: ");
    Serial.println(message);
    
    // Handle commands
    if (String(topic) == TOPIC_COMMAND) {
        if (message == "restart") {
            Serial.println("Restarting ESP32...");
            delay(1000);
            ESP.restart();
        } else if (message == "status") {
            publishStatus();
        }
    }
}

// ==================== SENSOR FUNCTIONS ====================

float readTemperature() {
    // Replace with your actual sensor reading
    // Example: return dht.readTemperature();
    return 25.0 + (random(-50, 50) / 10.0); // Simulated
}

float readHumidity() {
    // Replace with your actual sensor reading
    // Example: return dht.readHumidity();
    return 60.0 + (random(-100, 100) / 10.0); // Simulated
}

float readBatteryVoltage() {
    // Read battery voltage if applicable
    return 3.7 + (random(-20, 20) / 100.0); // Simulated
}

// ==================== PUBLISH FUNCTIONS ====================

void publishSensorData() {
    // Create JSON document
    StaticJsonDocument<256> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["temperature"] = round(readTemperature() * 10.0) / 10.0;
    doc["humidity"] = round(readHumidity() * 10.0) / 10.0;
    doc["battery"] = round(readBatteryVoltage() * 100.0) / 100.0;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    
    // Serialize JSON
    char buffer[256];
    serializeJson(doc, buffer);
    
    // Publish
    if (client.publish(TOPIC_SENSOR, buffer)) {
        Serial.println("Sensor data published:");
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
    Serial.println("\n🦟 Nyamuk ESP32 Starting...");
    
    // Connect to WiFi
    connectWiFi();
    
    // Configure MQTT
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqttCallback);
    client.setBufferSize(512);
    
    // Connect to MQTT
    connectMQTT();
    
    Serial.println("Setup complete!");
}

void loop() {
    // Ensure MQTT connection
    if (!client.connected()) {
        connectMQTT();
    }
    client.loop();
    
    // Publish sensor data at interval
    unsigned long now = millis();
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
        lastSensorRead = now;
        publishSensorData();
    }
    
    // Small delay
    delay(10);
}
