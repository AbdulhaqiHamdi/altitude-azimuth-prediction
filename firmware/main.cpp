#define ENABLE_USER_AUTH
#define ENABLE_DATABASE

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <FirebaseClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include "time.h"

// WiFi credentials
#define WIFI_SSID "XXX" // Fill with your WiFi SSID
#define WIFI_PASSWORD "XXX" // Fill with your WiFi Password

// Firebase project credentials
#define WEB_API_KEY "XXX" // Fill with your Firebase Web API Key
#define DATABASE_URL "XXX" // Fill with your Firebase Realtime Database URL
#define USER_EMAIL "XXX" // Fill with your Firebase User Email
#define USER_PASS "XXX" // Fill with your Firebase User Password

// NTP Server
const char* ntpServer = "pool.ntp.org";

// DHT Sensor settings
#define DHTPIN 14
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
float temperature, humidity;

// Firebase components
UserAuth user_auth(WEB_API_KEY, USER_EMAIL, USER_PASS);
FirebaseApp app;
WiFiClientSecure ssl_client;
using AsyncClient = AsyncClientClass;
AsyncClient aClient(ssl_client);
RealtimeDatabase Database;

// Firebase database paths
String uid;
String databasePath;
String tempPath = "/temperature";
String humPath = "/humidity";
String timePath = "/timestamp";
String parentPath;

// Timer
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 10000;//*6*10; // waktu pengambilan data
int timestamp;

// JSON object
object_t jsonData, obj1, obj2, obj3;
JsonWriter writer;

// Callback function
void processData(AsyncResult &aResult) {
  if (!aResult.isResult()) return;
  if (aResult.isEvent())
    Firebase.printf("Event: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.eventLog().message().c_str(), aResult.eventLog().code());
  if (aResult.isDebug())
    Firebase.printf("Debug: %s, msg: %s\n", aResult.uid().c_str(), aResult.debug().c_str());
  if (aResult.isError())
    Firebase.printf("Error: %s, msg: %s, code: %d\n", aResult.uid().c_str(), aResult.error().message().c_str(), aResult.error().code());
  if (aResult.available())
    Firebase.printf("Success: %s, payload: %s\n", aResult.uid().c_str(), aResult.c_str());
}

void initWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(" Connected!");
}

unsigned long getTime() {
  time_t now;
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return 0;
  time(&now);
  return now;
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  initWiFi();
  configTime(0, 0, ntpServer);

  // Tunggu waktu tersinkronisasi
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Waiting for NTP time sync...");
    delay(1000);
  }

  ssl_client.setInsecure();
  //ssl_client.setConnectionTimeout(1000);
  ssl_client.setHandshakeTimeout(5);

  initializeApp(aClient, app, getAuth(user_auth), processData, "authTask");
  app.getApp<RealtimeDatabase>(Database);
  Database.url(DATABASE_URL);
}

void loop() {
  app.loop();

  if (app.ready()) {
    unsigned long currentTime = millis();
    if (currentTime - lastSendTime >= sendInterval) {
      lastSendTime = currentTime;

      uid = app.getUid().c_str();
      databasePath = "/UsersData/" + uid + "/readings";
      static int baseTimestamp = 0;
      if (baseTimestamp == 0) {
        baseTimestamp = getTime();
      }
      timestamp = getTime();
      parentPath = databasePath + "/" + String(timestamp);

      temperature = dht.readTemperature();
      humidity = dht.readHumidity();

      if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor");
        return;
      }

      writer.create(obj1, tempPath, temperature);
      writer.create(obj2, humPath, humidity);
      writer.create(obj3, timePath, timestamp);
      writer.join(jsonData, 3, obj1, obj2, obj3);

      Database.set<object_t>(aClient, parentPath, jsonData, processData, "RTDB_Send_Data");

      Serial.printf("Temp: %.2f C, Humidity: %.2f %%\n", temperature, humidity);
    }
  }
}