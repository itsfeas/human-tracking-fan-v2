
/*
 Stepper Motor Control - one step at a time

 This program drives a unipolar or bipolar stepper motor.
 The motor is attached to digital pins 8 - 11 of the Arduino.

 The motor will step one step at a time, very slowly.  You can use this to
 test that you've got the four wires of your stepper wired to the correct
 pins. If wired correctly, all steps should be in the same direction.

 Use this also to count the number of steps per revolution of your motor,
 if you don't know it.  Then plug that number into the oneRevolution
 example to see if you got it right.

 Created 30 Nov. 2009
 by Tom Igoe

 */

#include <Stepper.h>
 

const int stepsPerRevolution = 800;  // change this to fit the number of steps per revolution
// for your motor

// initialize the stepper library on pins 8 through 11:
Stepper myStepper(stepsPerRevolution, 8, 9);


void setup() {
  // initialize the serial port:
  Serial.begin(9600);
  myStepper.setSpeed(1000);
}

void loop() {
  // step one step:
  if (Serial.available()>0){
    //Serial.print(Serial.readStringUntil('\n'));
    String message = Serial.readStringUntil('\n');
    if (message == "l01") {myStepper.setSpeed(1000); myStepper.step(2);}
    else if (message == "l02") {myStepper.setSpeed(1500); myStepper.step(4);}
    else if (message == "l03") {myStepper.setSpeed(1000); myStepper.step(6);}  
    else if (message == "l04") {myStepper.setSpeed(1000); myStepper.step(8);} 
    else if (message == "l05") {myStepper.setSpeed(1000); myStepper.step(10);}
    else if (message == "l10") {myStepper.setSpeed(1000); myStepper.step(6);}  
    else if (message == "l15") {myStepper.setSpeed(1000); myStepper.step(8);} 
    else if (message == "l20") {myStepper.setSpeed(1000); myStepper.step(10);}    
    else if (message == "r01") {myStepper.setSpeed(1000); myStepper.step(-2);}
    else if (message == "r02") {myStepper.setSpeed(1000); myStepper.step(-4);} 
    else if (message == "r03") {myStepper.setSpeed(1000); myStepper.step(-6);} 
    else if (message == "r04") {myStepper.setSpeed(1000); myStepper.step(-8);} 
    else if (message == "r05") {myStepper.setSpeed(1000); myStepper.step(-10);}
    else if (message == "r10") {myStepper.setSpeed(1000); myStepper.step(-6);} 
    else if (message == "r15") {myStepper.setSpeed(1000); myStepper.step(-8);} 
    else if (message == "r20") {myStepper.setSpeed(1000); myStepper.step(-10);}        
  }
  //delay(500);
}
