/*
 * Nyamuk ESP32 Advanced Template
 * 
 * Advanced ESP32 MQTT client with:
 * - Multiple sensor support
 * - OTA (Over-The-Air) updates
 * - Deep sleep mode
 * - WiFi reconnection
 * - MQTT reconnection
 * - Watchdog timer
 * 
 * Requirements:
 * - ESP32 board
 * - PubSubClient library
 * - ArduinoJson library
 * - ArduinoOTA library (built-in)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ArduinoOTA.h>

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
const char* DEVICE_ID = "esp32_advanced_001";

// Topic Configuration
const char* TOPIC_PREFIX = "nyamuk";
const char* TOPIC_SENSOR = "nyamuk/esp32_advanced_001/sensor";
const char* TOPIC_COMMAND = "nyamuk/esp32_advanced_001/command";
const char* TOPIC_STATUS = "nyamuk/esp32_advanced_001/status";
const char* TOPIC_OTA = "nyamuk/esp32_advanced_001/ota";

// Timing
const long SENSOR_INTERVAL = 10000; // 10 seconds
const long STATUS_INTERVAL = 60000; // 60 seconds
const long WATCHDOG_TIMEOUT = 30000; // 30 seconds

// ==================== GLOBAL OBJECTS ====================

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastSensorRead = 0;
unsigned long lastStatusPublish = 0;
unsigned long lastWifiCheck = 0;
unsigned long lastMqttCheck = 0;

// Watchdog
hw_timer_t *watchdogTimer = NULL;

// ==================== WATCHDOG FUNCTIONS ====================

void IRAM_ATTR watchdogISR() {
    // Reset ESP32 if watchdog triggers
    ESP.restart();
}

void setupWatchdog() {
    watchdogTimer = timerBegin(0, 80, true);
    timerAttachInterrupt(watchdogTimer, &watchdogISR, true);
    timerAlarmWrite(watchdogTimer, WATCHDOG_TIMEOUT * 1000, false);
    timerAlarmEnable(watchdogTimer);
}

void resetWatchdog() {
    if (watchdogTimer) {
        timerWrite(watchdogTimer, 0);
    }
}

// ==================== WIFI FUNCTIONS ====================

void connectWiFi() {
    if (WiFi.status() == WL_CONNECTED) {
        return;
    }
    
    Serial.print("Connecting to WiFi");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    WiFi.setAutoReconnect(true);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi connection failed!");
    }
}

// ==================== MQTT FUNCTIONS ====================

void connectMQTT() {
    if (client.connected()) {
        return;
    }
    
    Serial.print("Connecting to MQTT...");
    
    String clientId = "ESP32-" + String(DEVICE_ID);
    
    // Set Last Will Testament
    String willTopic = String(TOPIC_STATUS);
    String willMessage = "{\"status\":\"offline\",\"reason\":\"unexpected_disconnect\"}";
    
    if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD,
                       willTopic.c_str(), 1, true, willMessage.c_str())) {
        Serial.println("connected!");
        
        // Subscribe to command topic
        client.subscribe(TOPIC_COMMAND);
        
        // Publish online status
        client.publish(TOPIC_STATUS, "{\"status\":\"online\"}", true);
        
        // Publish OTA status
        client.publish(TOPIC_OTA, "{\"ota_available\":false}", true);
        
    } else {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.println(" retrying in 5 seconds");
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
    
    // Parse JSON command
    StaticJsonDocument<128> doc;
    if (deserializeJson(doc, message) == DeserializationOk) {
        const char* cmd = doc["command"];
        
        if (strcmp(cmd, "restart") == 0) {
            Serial.println("Restart command received");
            client.publish(TOPIC_STATUS, "{\"status\":\"restarting\"}", true);
            delay(1000);
            ESP.restart();
            
        } else if (strcmp(cmd, "status") == 0) {
            publishStatus();
            
        } else if (strcmp(cmd, "read") == 0) {
            publishSensorData();
            
        } else if (strcmp(cmd, "sleep") == 0) {
            int sleepTime = doc["seconds"] | 60;
            enterDeepSleep(sleepTime);
            
        } else if (strcmp(cmd, "config") == 0) {
            publishConfig();
        }
    }
}

// ==================== SENSOR FUNCTIONS ====================

float readTemperature() {
    // Replace with actual sensor
    return 25.0 + (random(-50, 50) / 10.0);
}

float readHumidity() {
    return 60.0 + (random(-100, 100) / 10.0);
}

float readBatteryVoltage() {
    // Read battery voltage if connected
    return 3.7 + (random(-20, 20) / 100.0);
}

// ==================== PUBLISH FUNCTIONS ====================

void publishSensorData() {
    StaticJsonDocument<384> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["temperature"] = round(readTemperature() * 10.0) / 10.0;
    doc["humidity"] = round(readHumidity() * 10.0) / 10.0;
    doc["battery"] = round(readBatteryVoltage() * 100.0) / 100.0;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["uptime"] = millis() / 1000;
    
    char buffer[384];
    serializeJson(doc, buffer);
    
    if (client.publish(TOPIC_SENSOR, buffer)) {
        Serial.println("Sensor data published");
    } else {
        Serial.println("Failed to publish sensor data");
    }
}

void publishStatus() {
    StaticJsonDocument<256> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["status"] = "online";
    doc["uptime"] = millis() / 1000;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["wifi_ssid"] = WiFi.SSID();
    doc["ip_address"] = WiFi.localIP().toString();
    doc["mac_address"] = WiFi.macAddress();
    doc["chip_model"] = ESP.getChipModel();
    doc["chip_revision"] = ESP.getChipRevision();
    doc["flash_size"] = ESP.getFlashChipSize();
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    client.publish(TOPIC_STATUS, buffer, true);
}

void publishConfig() {
    StaticJsonDocument<128> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["sensor_interval"] = SENSOR_INTERVAL;
    doc["status_interval"] = STATUS_INTERVAL;
    doc["watchdog_timeout"] = WATCHDOG_TIMEOUT;
    doc["mqtt_server"] = MQTT_SERVER;
    doc["mqtt_port"] = MQTT_PORT;
    
    char buffer[128];
    serializeJson(doc, buffer);
    
    client.publish(TOPIC_OTA, buffer);
}

// ==================== DEEP SLEEP ====================

void enterDeepSleep(int seconds) {
    Serial.printf("Entering deep sleep for %d seconds\n", seconds);
    
    // Publish sleep status
    client.publish(TOPIC_STATUS, "{\"status\":\"sleeping\"}", true);
    delay(100);
    
    // Configure wake up
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
    
    // Enter deep sleep
    esp_deep_sleep_start();
}

// ==================== OTA SETUP ====================

void setupOTA() {
    ArduinoOTA.setHostname(DEVICE_ID);
    
    ArduinoOTA.onStart([]() {
        String type;
        if (ArduinoOTA.getCommand() == U_FLASH) {
            type = "sketch";
        } else {
            type = "filesystem";
        }
        Serial.println("Start updating " + type);
        client.publish(TOPIC_OTA, "{\"ota_status\":\"updating\"}", true);
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("\nEnd");
        client.publish(TOPIC_OTA, "{\"ota_status\":\"complete\"}", true);
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        String errorMsg;
        if (error == OTA_AUTH_ERROR) errorMsg = "Auth Failed";
        else if (error == OTA_BEGIN_ERROR) errorMsg = "Begin Failed";
        else if (error == OTA_CONNECT_ERROR) errorMsg = "Connect Failed";
        else if (error == OTA_RECEIVE_ERROR) errorMsg = "Receive Failed";
        else if (error == OTA_END_ERROR) errorMsg = "End Failed";
        
        client.publish(TOPIC_OTA, "{\"ota_status\":\"error\",\"error\":\"" + errorMsg + "\"}", true);
    });
    
    ArduinoOTA.begin();
}

// ==================== SETUP & LOOP ====================

void setup() {
    Serial.begin(115200);
    Serial.println("\n🦟 Nyamuk Advanced ESP32 Starting...");
    
    // Setup watchdog
    setupWatchdog();
    
    // Connect to WiFi
    connectWiFi();
    
    // Setup OTA
    setupOTA();
    
    // Configure MQTT
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback(mqttCallback);
    client.setBufferSize(512);
    
    // Connect to MQTT
    connectMQTT();
    
    Serial.println("Advanced ESP32 ready!");
}

void loop() {
    // Reset watchdog
    resetWatchdog();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Check WiFi
    unsigned long now = millis();
    if (now - lastWifiCheck >= 10000) {
        lastWifiCheck = now;
        if (WiFi.status() != WL_CONNECTED) {
            connectWiFi();
        }
    }
    
    // Check MQTT
    if (now - lastMqttCheck >= 5000) {
        lastMqttCheck = now;
        if (!client.connected()) {
            connectMQTT();
        }
    }
    
    client.loop();
    
    // Publish sensor data
    if (now - lastSensorRead >= SENSOR_INTERVAL) {
        lastSensorRead = now;
        publishSensorData();
    }
    
    // Publish status
    if (now - lastStatusPublish >= STATUS_INTERVAL) {
        lastStatusPublish = now;
        publishStatus();
    }
    
    delay(10);
}
