/*
  Arduino Nano 33 BLE Getting Started
  BLE peripheral with a simple Hello World greeting service that can be viewed
  on a mobile phone
  Adapted from Arduino BatteryMonitor example
*/

//https://www.okdo.com/getting-started/get-started-with-arduino-nano-33-ble/

#include <ArduinoBLE.h>
#include <Wire.h>
#include <LSM303.h>
#include <L3G.h>

LSM303 compass;

BLEService gloveService("fff0");  // User defined service

BLEIntCharacteristic finger0("ccc0", BLERead | BLENotify);
BLEIntCharacteristic finger1("ccc1", BLERead | BLENotify);
BLEIntCharacteristic finger2("ccc2", BLERead | BLENotify);
BLEIntCharacteristic finger3("ccc3", BLERead | BLENotify);

BLEIntCharacteristic accelx("aaa1", BLERead | BLENotify);
BLEIntCharacteristic accely("aaa2", BLERead | BLENotify);
BLEIntCharacteristic accelz("aaa3", BLERead | BLENotify);

void setup() {
  Serial.begin(9600);    // initialize serial communication
  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin
  while (!Serial);

  Wire.begin();
  if (!compass.init()) {
    Serial.println("Failed to connect compass!");
    while (1);
  }
  compass.enableDefault();

  if (!BLE.begin()) {   // initialize BLE
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE");  // Set name for connection
  BLE.setAdvertisedService(gloveService); // Advertise service
  gloveService.addCharacteristic(finger0);
  gloveService.addCharacteristic(finger1);
  gloveService.addCharacteristic(finger2);
  gloveService.addCharacteristic(finger3);
  gloveService.addCharacteristic(accelx);
  gloveService.addCharacteristic(accely);
  gloveService.addCharacteristic(accelz);
  BLE.addService(gloveService); // Add service

  BLE.advertise();  // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections...");
}

void read_compass() {
  compass.read();
  int ax = int(compass.a.x >> 4); // convert to units of (mg)
  int ay = int(compass.a.y >> 4);
  int az = int(compass.a.z >> 4);
  accelx.setValue(ax);
  accely.setValue(ay);
  accelz.setValue(az);
  Serial.println("Ax: "+String(ax)+", Ay: "+String(ay)+", Az: "+String(az));
}

void read_flex() {
  int flex0 = analogRead(A0);
  int flex1 = analogRead(A1);
  int flex2 = analogRead(A2);
  int flex3 = analogRead(A3);
  finger0.setValue(flex0);
  finger1.setValue(flex1);
  finger2.setValue(flex2);
  finger3.setValue(flex3);
  Serial.println("flex0: "+String(flex0)+", flex1: "+String(flex1)+", flex2: "+String(flex2)+", flex3: "+String(flex3));
}

// void read_gyro() {
//   int gyroX = int(gyro.g.x * 8.75/1000); // convert to units of (mdps) = mill-degrees per second; divide by 1000 to convert to degrees
//   int gyroY = int(gyro.g.y * 8.75/1000);
//   int gyroZ = int(gyro.g.z * 8.75/1000);
//   gyro.read();
//   gyrox.setValue(gyroX);
//   gyroy.setValue(gyroY);
//   gyroz.setValue(gyroZ);
//   Serial.println("Gx: "+String(gyroX)+", Gy: "+String(gyroY)+", Gz: "+String(gyroZ));
// }

void loop() {
  BLEDevice central = BLE.central();  // Wait for a BLE central to connect

  // if a central is connected to the peripheral:
  if (central) {
    Serial.print("Connected to central MAC: ");
    // print the central's BT address:
    Serial.println(central.address());
    // turn on the LED to indicate the connection:
    digitalWrite(LED_BUILTIN, HIGH);

    int count = 0;
    while (central.connected()){
      delay(100);
      read_compass();
      delay(100);
      read_flex();
    } // keep looping while connected
    
    // when the central disconnects, turn off the LED:
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("Disconnected from central MAC: ");
    Serial.println(central.address());
  }
}
