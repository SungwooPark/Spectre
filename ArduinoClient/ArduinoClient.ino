/* Arduino Client - v1.1 (Principles of Engineering)*/
/* Supports handshake process */
/* Upcoming changes: v1.2 - supports window.py serial protocol*/


/* General Libraries */
#include <Wire.h>
#include <Adafruit_MotorShield.h> // for access to the motor shield
#include "utility/Adafruit_MS_PWMServoDriver.h" // for interfacing with the motor

/* Motor and Shield Objects */
// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

// Motor 3 -> right spindle
Adafruit_DCMotor *motorBaseR = AFMS.getMotor(3);
// Motor 1 -> left spindle
Adafruit_DCMotor *motorBaseL = AFMS.getMotor(1);

unsigned long previousTime = 0;  // initialize time check variable
unsigned long interval = 300; // 2 second response time for mechanization
int spd = 150;
char incomingBit = '2'; // default is 2, does nothing

void setup() {
  // Begin baud transmissions at 9600 bps
  Serial.begin(9600);
  // Begin I2C transmission at default frequency = 1.6 KHz
  AFMS.begin();
  }

// Generic functions for operations
void test_forward(Adafruit_DCMotor *motorBase) {

  // Assumes forward motion
  motorBase->run(FORWARD);
  //motorRight->run(FORWARD);

  // Implements speed settings into motors for execution
  motorBase->setSpeed(spd);
  //motorRight->setSpeed(spd);
}

void terminate(Adafruit_DCMotor *motorBase){
  // Releases motors
  motorBase->run(RELEASE);
  //motorRight->run(RELEASE);
}

void test_backward(Adafruit_DCMotor *motorBase) {

  // Assumes rear motion
  motorBase->run(BACKWARD);
  //motorRight->run(BACKWARD);

  // Implements speed settings into motors for execution
  motorBase->setSpeed(spd);
  //motorRight->setSpeed(spd);
}

void receiveSerial(){
  if (Serial.available() > 0){
    // reading incoming bit data
    incomingBit = Serial.read(); // reads as character
    /*if(Serial.read() == '2')
    {
      test_forward(motorBase);
      delay(100);
      test_backward(motorBase);
      delay(100);
    }*/
  }
}

/*void closeSequencetest(){
  Serial.println("Now closing");
  test_forward(motorBaseR); // ACW motion
  test_forward(motorBaseL); // CW motion
  delay(2000);
  terminate(motorBaseR);
  terminate(motorBaseL);
}

void openSequencetest(){
  Serial.println("Now opening");
  test_backward(motorBaseR); // CW
  test_backward(motorBaseL); // ACW motion
  delay(2000);
  terminate(motorBaseR);
  terminate(motorBaseL);
}*/

void loop() {
  // v1.3 : updated class
  receiveSerial();
  unsigned long currentTime = millis();

  // for testing
  /*openSequencetest();
  if(currentTime - previousTime >= interval)
  {
  closeSequencetest();
  }*/

  switch(incomingBit){
    case '0':
      // Close -> 0

      // Joins the two sub-mirrors
      //Serial.print("Opening");
      //Serial.println(" ");
      test_forward(motorBaseR);
      test_forward(motorBaseL);
      break;
    case '1':
      // Open -> 1
      // Separates the two sub-mirrors

      //Serial.print("Closing");
      //Serial.println(" ");
      test_backward(motorBaseR);
      test_backward(motorBaseL);
      break;
    default:
      // 2 is initialized @ beginning
      if(currentTime - previousTime >= interval)
      {
        previousTime = currentTime;
        terminate(motorBaseR);
        terminate(motorBaseL);
      }
      break;
  }
}
