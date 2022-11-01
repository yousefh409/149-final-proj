/*
  Arduino Nano 33 BLE Getting Started
  BLE peripheral with a simple Hello World greeting service that can be viewed
  on a mobile phone
  Adapted from Arduino BatteryMonitor example
*/

//https://www.okdo.com/getting-started/get-started-with-arduino-nano-33-ble/

#include <ArduinoBLE.h>

BLEService gloveService("fff0");  // User defined service

BLEIntCharacteristic gloveCharacteristic("ccc0",  // standard 16-bit characteristic UUID
    BLERead | BLENotify); // remote clients will only be able to read this

BLEIntCharacteristic finger1("ccc1", BLERead | BLENotify);
BLEIntCharacteristic finger2("ccc2", BLERead | BLENotify);
BLEIntCharacteristic finger3("ccc3", BLERead | BLENotify);
BLEIntCharacteristic finger4("ccc4", BLERead | BLENotify);

void setup() {
  Serial.begin(9600);    // initialize serial communication
  while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin

  if (!BLE.begin()) {   // initialize BLE
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE");  // Set name for connection
  BLE.setAdvertisedService(gloveService); // Advertise service
  gloveService.addCharacteristic(gloveCharacteristic); // Add characteristic to service
  gloveService.addCharacteristic(finger1);
  gloveService.addCharacteristic(finger2);
  gloveService.addCharacteristic(finger3);
  gloveService.addCharacteristic(finger4);
  BLE.addService(gloveService); // Add service

  BLE.advertise();  // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections...");
}

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
      delay(250);
      gloveCharacteristic.setValue(count);
      count += 1;
    } // keep looping while connected
    
    // when the central disconnects, turn off the LED:
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print("Disconnected from central MAC: ");
    Serial.println(central.address());
  }
}
