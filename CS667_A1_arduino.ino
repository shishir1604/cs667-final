#include <SoftwareSerial.h>
#include <DHT.h>
//#include <ArduinoJson.h>

//ultrasonic sensor
#define trigger 10
#define echo 9
#define yellow 4


//PIR motion sensor
#define PIR 8
#define green 3
int state=LOW;

//DHT sensor
#define dhtpin 11
#define red 2
DHT dht = DHT(dhtpin, DHT11);


//global variables
int humidity=0;
int temp=0;
float distance_cm=0.0;
float distance_inch=0.0;

//setup arduino to nodemcu
SoftwareSerial nodemcu(5,6);   //5-rx, 6-tx


void setup() {
  // put your setup code here, to run once:
  
  Serial.begin(9600);
  nodemcu.begin(9600);
  delay(1000);

  dht.begin();
  pinMode(trigger,OUTPUT);
  digitalWrite(trigger,LOW);
  pinMode(echo,INPUT);
  pinMode(PIR,INPUT);
  pinMode(red,OUTPUT);
  pinMode(yellow,OUTPUT);
  pinMode(green,OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  dht11();
  ultrasonic();
  pir();
  
  String data = String(temp) + "," + String(humidity) + "," + String(distance_cm) + "," + String((state == HIGH) ? "YES" : "NO");

  // Send data to NodeMCU
  nodemcu.println(data);

//print data in serial monitor
  Serial.print("distance_cm: ");
  Serial.print(distance_cm);
  Serial.print("  ");
  Serial.print("distance_inch: ");
  Serial.println(distance_inch);

  Serial.print("humidity: ");
  Serial.print(humidity);
  Serial.print("  ");
  Serial.print("temperature: ");
  Serial.println(temp);
  
//  StaticJsonDocument<1024> data;
////  data["ultrasonic"]= distance_cm ;
//  data["temperature"]= temp;
//  data["humidity"]= humidity;
  if(state==HIGH){
    Serial.println("Motion detected!");
////    data["motion"]=1;}
  }
  else {
    Serial.println("No motion");
////    data["motion"]=0;}

  }
  Serial.println("");
//  serializeJson(data,nodemcu);
//  nodemcu.println(); //
//  delay(500);

  delay(500);    //wait for data to transmit

}


void ultrasonic(){
  digitalWrite(trigger,HIGH);
  delay(10);      
  digitalWrite(trigger,LOW);

  long duration=pulseIn(echo,HIGH);
  distance_cm= duration*0.0343/2;  //in cm
  distance_inch= distance_cm*0.394;  //in inches

  if (distance_cm >20){
    digitalWrite(yellow,LOW);
  }
  else{
    digitalWrite(yellow,HIGH);
  }
}

void dht11(){
  humidity= dht.readHumidity();
  temp= dht.readTemperature();
  if (temp>30){
    digitalWrite(red,HIGH);
  }
  else{
    digitalWrite(red,LOW);
  }
}

void pir(){
  state = digitalRead(PIR);
  if (state==HIGH){
    digitalWrite(green,HIGH);
  }
  else {
    digitalWrite(green,LOW);
  }
}
