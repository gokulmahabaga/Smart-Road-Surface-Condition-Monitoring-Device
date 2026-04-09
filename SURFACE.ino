#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

/* WiFi */
const char* ssid = "pemchip";
const char* password = "pemchip@19";

/* Server */
ESP8266WebServer server(80);

/* Sensor */
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

/* Data from Streamlit */
String roadData = "No Data";

/* ---------------- HOME PAGE ---------------- */
void handleRoot() {
  sensors_event_t event;
  accel.getEvent(&event);

  String html = "<html><head>";
  html += "<meta http-equiv='refresh' content='2'>";

  html += "<style>";
  html += "body{font-family:Arial;background:#0f172a;color:white;text-align:center;margin:0;padding:0;}";
  html += ".title{font-size:28px;font-weight:bold;padding:20px;}";
  html += ".container{display:flex;justify-content:center;flex-wrap:wrap;gap:20px;margin-top:20px;}";
  html += ".card{background:#1e293b;padding:20px;border-radius:15px;min-width:300px;box-shadow:0 0 15px rgba(0,0,0,0.6);}";
  html += ".label{color:#38bdf8;font-size:18px;margin-bottom:10px;font-weight:bold;}";
  html += ".value{font-size:16px;margin:6px 0;}";
  html += ".status{color:#22c55e;font-weight:bold;}";
  html += "</style>";

  html += "</head><body>";

  html += "<div class='title'>Smart Road Monitoring System</div>";

  html += "<div class='container'>";

  /* AI DATA CARD */
  html += "<div class='card'>";
  html += "<div class='label'>AI Detection Output</div>";
  html += "<div class='value'>" + roadData + "</div>";
  html += "</div>";

  /* SENSOR DATA CARD */
  html += "<div class='card'>";
  html += "<div class='label'>Vibration Sensor (ADXL345)</div>";
  html += "<div class='value'>X: " + String(event.acceleration.x) + "</div>";
  html += "<div class='value'>Y: " + String(event.acceleration.y) + "</div>";
  html += "<div class='value'>Z: " + String(event.acceleration.z) + "</div>";
  html += "</div>";

  html += "</div>";

  html += "</body></html>";

  server.send(200, "text/html", html);
}

/* ---------------- STREAMLIT DATA RECEIVER ---------------- */
void handleData() {
  if (server.hasArg("value")) {
    roadData = server.arg("value");
    Serial.println("Updated: " + roadData);
  }
  server.send(200, "text/plain", "OK");
}

/* ---------------- JSON API ---------------- */
void handleAPI() {
  sensors_event_t event;
  accel.getEvent(&event);

  String json = "{";
  json += "\"road\":\"" + roadData + "\",";
  json += "\"x\":" + String(event.acceleration.x) + ",";
  json += "\"y\":" + String(event.acceleration.y) + ",";
  json += "\"z\":" + String(event.acceleration.z);
  json += "}";

  server.send(200, "application/json", json);
}

/* ---------------- SETUP ---------------- */
void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  Wire.begin(D2, D1);

  if (!accel.begin()) {
    Serial.println("ADXL345 not found!");
    while (1);
  }

  accel.setRange(ADXL345_RANGE_16_G);

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.on("/api", handleAPI);

  server.begin();
  Serial.println("HTTP Server Started");
}

/* ---------------- LOOP ---------------- */
void loop() {
  server.handleClient();
}
