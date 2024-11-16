#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Define your Wi-Fi and MQTT credentials
const char* ssid = "XP6";
const char* password = "hellobuddy";
const char* mqtt_server = "172.23.7.99";
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor/data";

// SoftwareSerial for communication with Arduino Uno
SoftwareSerial nodemcu(D6, D5);  // D6-RX, D5-TX

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("NodeMCUClient")) {
      Serial.println("connected");
    } else {
      Serial.print("failed ");
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  nodemcu.begin(9600);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (nodemcu.available()) {
    String data = nodemcu.readStringUntil('\n');
    String data1= data;
    data.replace(',','a');                  //sometimes utf-8 fails to decode special character(,)
    client.publish(mqtt_topic,data.c_str());

    //verify if data is properly transmitted
    Serial.print("Published data: ");
    Serial.println(data1);  
  }

  delay(500);
}
