#include <Servo.h>
#include <stdlib.h>
#include <math.h>

Servo s0;
Servo s1;
Servo s2;
Servo s3;
Servo s4;
Servo s5;
Servo s6;
Servo s7;
Servo s8;
Servo s9;
Servo s10;
Servo s11;
Servo s12;
Servo s13;

int pos = 0;
int pin = 0;
void setup() {
  s0.attach(0);
  s1.attach(1);
  s2.attach(2);
  s3.attach(3);
  s4.attach(4);
  s5.attach(5);
  s6.attach(6);
  s7.attach(7);
  s8.attach(8);
  s9.attach(9);
  s10.attach(10);
  s11.attach(11);
  s12.attach(12);
  s13.attach(13);
  Serial.begin(500000);
  //Serial.begin(115200);
  Serial.setTimeout(1);
  s2.write(180);
}

void loop() {
  if (Serial.available()) {
    unsigned long val = Serial.readString().toInt();
    if (val >= 100000 && val < 110000){
      int etat = val % 2;
      int pin = (val-100000-etat)/100;
      digitalWrite(pin, etat);
    }
    else if (val >= 110000 && val < 120000){
      int pin = val-110000;
      int read_ = analogRead(pin);
      Serial.println(read_);
    }
    else if (val >= 120000 && val < 130000){
      int pin = val-120000;
      pinMode(pin, INPUT);
      int read_ = digitalRead(pin);
      Serial.println(read_);
    }
    else if (val >= 130000 && val < 140000){
      int etat = val % 2;
      int pin = val-130000-etat;
      pin = pin/100;
      //etat = 1 : OUTPUT  et etat = 0 : INPUT
      if (etat == 0){
        pinMode(pin, INPUT);
      }
      else if (etat == 1){
      Serial.println(pin);
        pinMode(pin, OUTPUT);  
      }
    }
    else if (val >= 200000 && val < 300000){
      val = val-200000;
      int pin = int(val/1000);
      int valeur = val - (pin*1000);
      Serial.println(valeur);
      analogWrite(pin, valeur);
    }
    else{
      pin = floor(val/1000);
      pos = val - (pin * 1000); 
      if (pin == 0) {
        s0.write(pos);
        Serial.write("0 :: ");
        Serial.write(pos);
      }
      else if (pin == 1) {
        s1.write(pos);
        Serial.write("1 :: ");
        Serial.write(pos);
      }
      else if (pin == 2) {
        s2.write(pos);
        Serial.write("2 :: ");
        Serial.write(pos);
      }
      else if (pin == 3) {
        s3.write(pos);
        Serial.write("3 :: ");
        Serial.write(pos);
      }
      else if (pin == 4) {
        s4.write(pos);
        Serial.write("4 :: ");
        Serial.write(pos);
      }
      else if (pin == 5) {
        s5.write(pos);
        Serial.write("5 :: ");
        Serial.write(pos);
      }
      else if (pin == 6) {
        s6.write(pos);
        Serial.write("6 :: ");
        Serial.write(pos);
      }
      else if (pin == 7) {
        s7.write(pos);
        Serial.write("7 :: ");
        Serial.write(pos);
      }
      else if (pin == 8) {
        s8.write(pos);
        Serial.write("8 :: ");
        Serial.write(pos);
      }
      else if (pin == 9) {
        s9.write(pos);
        Serial.write("9 :: ");
        Serial.write(pos);
      }
      else if (pin == 10) {
        s10.write(pos);
        Serial.write("10 :: ");
        Serial.write(pos);
      }
      else if (pin == 11) {
        s11.write(pos);
        Serial.write("11 :: ");
        Serial.write(pos);
      }
      else if (pin == 12) {
        s12.write(pos);
        Serial.write("12 :: ");
        Serial.write(pos);
      }
      else if (pin == 13) {
        s13.write(pos);
        Serial.write("13 :: ");
        Serial.write(pos);
      }}
}
}
