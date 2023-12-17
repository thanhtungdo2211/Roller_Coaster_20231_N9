#include <Arduino.h>
#include "Servo.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define a 14
// #define b 27
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define TIEMCAN 35
unsigned long thoigian;
unsigned long hientai;
int timecho = 976;
const int weight = 1500; // defines the weight is 1500 kgs
int caseTrack = 0; // thể hiện đang ở địa hình nào
int isLeftRound = 0; // Đang ở nửa đường tròn nào, bên trái hay bên phải




int demxung = 0;
// int demxunglen = 0;
// int demxungxuong = 0;
float rpm = 0;
float tocdo = 0;
// int tiemcan = 0;


// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Pin Definitions
#define BRUSHLESSMOTOR_PIN_DATA	19

// Global variables and defines
const int brushlessMotorLowSpeed = 1000;  //Starting speed
const int brushlessMotorFastSpeed = 2000; //Top speed
// object initialization
Servo brushlessMotor;

// define vars for testing menu
const int timeout = 10000;       //define timeout of 10 sec
char menuOption = 0;
long time0;


int count = 0; // trễ vận tốc
int countRoundState = 0; // phụ trợ chuyển đổi nửa vòng trái sang nửa vòng phải
int controll = 1090;

// void dem_xung_len()
// {
//   demxunglen++;
//   // Serial.println(demxunglen);
// }
void dem_xung()
{
  demxung++;
  // Serial.println(demxung);
}
// void dem_xung_xuong()
// {
//   demxungxuong++;
//   //  Serial.println(demxungxuong);
// }
// void IRAM_ATTR tiemcan()
// {
//   //Serial.println("Train's coming");
//   demxung++;
// }
void setup() {
  // put your setup code here, to run once:
  // Setup Serial which is useful for debugging
  // Use the Serial Monitor to view printed messages
    Serial.begin(9600);
    while (!Serial) ; // wait for serial port to connect. Needed for native USB
    Serial.println("start");
    pinMode(a, INPUT);
    // pinMode(b, INPUT);
    pinMode(TIEMCAN, INPUT_PULLUP);
    // attachInterrupt(a, dem_xung_xuong, FALLING);
    // attachInterrupt(b, dem_xung_len, RISING); 
    attachInterrupt(a, dem_xung, CHANGE); 
    // attachInterrupt(TIEMCAN, tiemcan, FALLING);
  // WARNING! DO NOT CONNECT THE PROPELLER UNDER TEST!
    brushlessMotor.attach(BRUSHLESSMOTOR_PIN_DATA);
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    // for (;;);
  }
  delay(2000);
//  display.setFont(&FreeSerif9pt7b); // text-font
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 20);
  display.display();

}

void loop() {
  thoigian = millis();
  if (thoigian - hientai >= timecho) {    
    hientai = thoigian;
    rpm = (demxung/40)*60;    
    tocdo = float(demxung/40)*float(2*0.05*3.14)*3.6; 
    // rpm = (demxung/40)*60;
    // tocdo = float((demxung/40)*(2*0.09*3.14));
    // demxungxuong = 0;
    demxung=0;
    int tiemcan = digitalRead (TIEMCAN);
    Serial.println(tiemcan);
    if (tiemcan == 0 && caseTrack == 0){
      caseTrack +=1;
      Serial.println("Train's coming");
    }
    // Serial.println(thoigian);
    // Serial.print("\t\t\t\t"); Serial.print("RPM: "); Serial.print(rpm);
    // Serial.print("   "); Serial.print("km/h: "); Serial.println(tocdo); 
    display.clearDisplay();

   }

  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);

// //toc do
  display.print("Speed: ");
  display.print(tocdo);
  display.print(" km/h\n");
  display.setCursor(0,20);

//khoi luong
  display.print("Weigh: ");
  display.print(1500);
  display.print(" kg\n");
  brushlessMotor.writeMicroseconds(1090);

  // put your main code here, to run repeatedly:
  if(caseTrack == 0)
  {
  //vị trí
  display.print("Location: ");
  display.print("Dang xuong doc");
  display.print("\n");
  display.print("Require: ");
  display.print("87 km/h");
  display.print("\n");
  brushlessMotor.writeMicroseconds(controll);
  if(count >= 30 && tocdo <= 87) {
    count = 0;
    controll += 5; 
    Serial.println(controll);
  }
  count ++;
  }
  if(caseTrack == 1) {
    display.print("Dang o loop 1 ");
    display.print("\n");
    if(isLeftRound == 0){
      display.print("Dinh loop <= ");
    display.print("31.8 km/h");
    display.print("\n");
    
    
  brushlessMotor.writeMicroseconds(controll);
    if(count >= 30 && tocdo >=31.8) {
    count = 0;
    controll -= 5; 
    Serial.println(controll);
  }
  }
  count ++;
  if(tocdo <= 31.8) {
    countRoundState ++;
  }
  if(countRoundState >= 30){
    isLeftRound = 1;
    countRoundState = 0;
  } 
  if(isLeftRound == 1 ) {
    display.print("Chan loop >= ");
    display.print("60 km/h");
    display.print("\n");
  if(count >= 30 && tocdo <= 60) {
    count = 0;
    controll +=5;
    Serial.println(controll);
  }
  }
  }
  if(caseTrack == 2) {
    display.print("Dang o track 3 ");
    display.print("\n");
      display.print("Track 3 <= ");
    display.print("41.8 km/h");
    display.print("\n");
    brushlessMotor.writeMicroseconds(controll);
    if(tocdo >= 41.8) {
    count = 0;
    controll -=5;
    Serial.println(controll);
  }
  }
  if(caseTrack == 3) {
    display.print("Dang o loop 4 ");
    display.print("\n");
      display.print("Track 3 <= ");
    display.print("41.8 km/h");
    display.print("\n");
    brushlessMotor.writeMicroseconds(controll);
  if(count >= 30 && tocdo <= 80) {
    count = 0;
    controll += 5; 
    Serial.println(controll);
  }
  count ++;
  }
  if(caseTrack == 4) {
     display.print("Dang o track 5 ");
    display.print("\n");
      display.print("Track 5 <= ");
    display.print("41.8 km/h");
    display.print("\n");
    brushlessMotor.writeMicroseconds(controll);
    if(tocdo >= 41.8) {
    count = 0;
    controll -=5;
    Serial.println(controll);
  }
  }
  display.display();

}


