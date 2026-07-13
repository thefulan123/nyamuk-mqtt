/*
 * Nyamuk ESP32 DHT22 Template
 * 
 * ESP32 MQTT client that reads temperature and humidity from DHT22 sensor
 * and publishes to your Nyamuk-managed Mosquitto broker.
 * 
 * Requirements:
 * - ESP32 board
 * - DHT22 sensor connected to GPIO4
 * - PubSubClient library
 * - ArduinoJson library
 * - DHT sensor library by Adafruit
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

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
const char* DEVICE_ID = "esp32_dht22_001";

// DHT Sensor Configuration
#define DHTPIN 4
#define DHTTYPE DHT22

// Topic Configuration
const char* TOPIC_SENSOR = "nyamuk/esp32_dht22_001/sensor";
const char* TOPIC_COMMAND = "nyamuk/esp32_dht22_001/command";
const char* TOPIC_STATUS = "nyamuk/esp32_dht22_001/status";
const char* TOPIC_ALERT = "nyamuk/esp32_dht22_001/alert";

// ==================== GLOBAL OBJECTS ====================

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

unsigned long lastSensorRead = 0;
const long SENSOR_INTERVAL = 10000; // 10 seconds

// Alert thresholds
const float TEMP_HIGH = 35.0;
const float TEMP_LOW = 15.0;
const float HUMIDITY_HIGH = 80.0;
const float HUMIDITY_LOW = 30.0;

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
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float heatIndex = dht.computeHeatIndex(temperature, humidity, false);
    float fahrenheit = dht.readTemperature(true);
    
    // Check if reads failed
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }
    
    StaticJsonDocument<320> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["temperature_c"] = round(temperature * 10.0) / 10.0;
    doc["temperature_f"] = round(fahrenheit * 10.0) / 10.0;
    doc["humidity"] = round(humidity * 10.0) / 10.0;
    doc["heat_index_c"] = round(heatIndex * 10.0) / 10.0;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    
    char buffer[320];
    serializeJson(doc, buffer);
    
    if (client.publish(TOPIC_SENSOR, buffer)) {
        Serial.println("DHT22 data published:");
        Serial.println(buffer);
        
        // Check for alerts
        checkAlerts(temperature, humidity);
    }
}

void checkAlerts(float temperature, float humidity) {
    if (temperature > TEMP_HIGH) {
        client.publish(TOPIC_ALERT, "{\"alert\":\"temperature_high\",\"value\":" + String(temperature) + "}");
    } else if (temperature < TEMP_LOW) {
        client.publish(TOPIC_ALERT, "{\"alert\":\"temperature_low\",\"value\":" + String(temperature) + "}");
    }
    
    if (humidity > HUMIDITY_HIGH) {
        client.publish(TOPIC_ALERT, "{\"alert\":\"humidity_high\",\"value\":" + String(humidity) + "}");
    } else if (humidity < HUMIDITY_LOW) {
        client.publish(TOPIC_ALERT, "{\"alert\":\"humidity_low\",\"value\":" + String(humidity) + "}");
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
    Serial.println("\n🦟 Nyamuk DHT22 Sensor Starting...");
    
    // Initialize DHT sensor
    dht.begin();
    
    // Connect to WiFi
    connectWiFi();
    
    // Configure MQTT
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqttCallback);
    client.setBufferSize(512);
    
    // Connect to MQTT
    connectMQTT();
    
    Serial.println("DHT22 sensor ready!");
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
