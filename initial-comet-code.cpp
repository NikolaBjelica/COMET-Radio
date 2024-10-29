#include "Arduino.h"
#include "DRV8825.h"

#define MOTOR_STEPS 200

#define DIR_1 19
#define STEP_1 4
#define SLEEP_1 32
#define RESET_1 32

#define DIR_2 13
#define STEP_2 14
#define SLEEP_2 27
#define RESET_2 27

#define LIMIT_SWITCH 34  // Pin for the limit switch (must be interrupt-capable)

enum commands 
{
  STOP = 0x00,
  RESET = 0x01,
  SET = 0x02,
  TRACK = 0x03,
  SPEED = 0x04,
  AXIS = 0x05,
  ANGLE = 0x06,
  RESETSYSTEM = 0x07
};

DRV8825 stepper1(MOTOR_STEPS, DIR_1, STEP_1);
DRV8825 stepper2(MOTOR_STEPS, DIR_2, STEP_2);

// Variables to track the motor state
volatile bool stopMotors = false;
volatile bool limitSwitchPressed = false;  // To track if the switch is pressed or released

bool moveReverseX = false;
bool moveReverseY = false;

bool movingAlongX = false;
bool movingAlongY = false;

int stopY = 0;
int tracking = 0;
int angleSet = 0;
int axisSet = 0;
int speedSet = 0;

float secondsBetweenMovement = 0.0;
float angleBetweenMovement = 0.0;

float stepperXDegrees = 0.0;
float stepperYDegrees = 0.0;

float pastTime = 0.0;
float currentTime = 0.0;
bool pastTimeTaken = false;

// Function to stop the motors
void stopAllMotors() 
{
  stepper1.stop();
  stepper2.stop();
  Serial.println("Motors stopped.");
  tracking = 0;
  angleSet = 0;
  axisSet = 0;
  speedSet = 0;
  pastTimeTaken = false;
}

void handleMotorSwitchCase() 
{
  stepper2.stop();
  stopY = 1;
  Serial.print(stopY);
  Serial.println("Y Motor hit the limit switch");
}

void resetAllMotors() 
{
  resetXMotor();
  resetYMotor();
  Serial.println("Both motors reset to initial positions.");
}

/*void doTracking() 
{
  if (stepperXDegrees == 180)
  {
    moveReverseX = true;
  }

  if (stepperXDegrees == -180)
  {
    moveReverseX = false;
  }

  if (stepperYDegrees == 90)
  {
    moveReverseY = true;
  }

  if (stepperYDegrees == -90)
  {
    moveReverseY = false;
  }

  if (false == moveReverseX) 
  {
    stepper1.rotate(10);
    stepperXDegrees += 10;
    Serial.print("stepperXDegrees: ");
    Serial.println(stepperXDegrees);  // Correct way to print float value
  } 
  else 
  {
    stepper1.rotate(-10);
    stepperXDegrees -= 10;
    Serial.print("stepperXDegrees: ");
    Serial.println(stepperXDegrees);  // Correct way to print float value
  }

  if (false == moveReverseY && stopY != 1) 
  {
    stepper2.rotate(10);
    stepperYDegrees += 10;
    Serial.print("stepperYDegrees: ");
    Serial.println(stepperYDegrees);  // Correct way to print float value
  } 
  else if (true == moveReverseY && stopY != 1)
  {
    stepper2.rotate(-10);
    stepperYDegrees -= 10;
    Serial.print("stepperYDegrees: ");
    Serial.println(stepperYDegrees);  // Correct way to print float value
  }

  delay(1000);
}*/

void doTracking()
{
  if (!pastTimeTaken)
  {
    pastTime = millis();
    pastTime /= 1000;
    pastTimeTaken = true;
  }

  currentTime = millis();
  currentTime /= 1000;

  float totalTimeElapsed = currentTime - pastTime;

  /*Serial.println(currentTime);
  Serial.println(pastTime);
  Serial.println(totalTimeElapsed);*/

  if (totalTimeElapsed >= secondsBetweenMovement)
  {
    if (movingAlongX)
    {
      stepper1.rotate(angleBetweenMovement);
      stepperXDegrees += angleBetweenMovement;
      Serial.println(stepperXDegrees);
    }
    else if (movingAlongY)
    {
      stepper2.rotate(angleBetweenMovement);
      stepperYDegrees += angleBetweenMovement;
      Serial.println(stepperYDegrees);
    }
    pastTime = currentTime;
    pastTimeTaken = false;
  }
}

void setInitalMotors() 
{
  bool settingMotors = true;
  
  while (settingMotors) 
  {
    Serial.println("What angle would you want to set for the X Motor?");
    while (Serial.available() == 0) {}
    float x_angle = Serial.parseFloat();

    Serial.println(x_angle);

    Serial.println("What angle would you want to set for the Y Motor?");
    while (Serial.available() == 0) {}
    float y_angle = Serial.parseFloat();

    Serial.println(y_angle);

    unsigned long StartTime = millis();

    setMotorX(x_angle);
    setMotorY(y_angle);

    Serial.println("Satisfied?\n\r 0 for Yes\n\r 1 for No\n");
    while (Serial.available() == 0) {}
    int response = Serial.parseInt();

    if (0 == response) 
    {
      settingMotors = false;
    }
  }
}

void setMotorX(float newDegrees) 
{
  Serial.println("In here setMotorX");
  float delta = newDegrees - stepperXDegrees;  
  stepper1.rotate(delta);
  stepperXDegrees = newDegrees;
}

void setMotorY(float newDegrees) 
{
  Serial.println("In here setMotorY");
  float delta = newDegrees - stepperYDegrees;  
  stepper2.rotate(delta);
  stepperYDegrees = newDegrees;
}

void resetXMotor() 
{
  stepper1.rotate(-1 * stepperXDegrees);  // Rotate back to zero degrees
  stepperXDegrees = 0;
}

void resetYMotor() 
{
  stepper2.rotate(-1 * stepperYDegrees);  // Rotate back to zero degrees
  stepperYDegrees = 0;
}

void setup() 
{
  Serial.begin(9600);
  
  // Initialize the stepper motors
  stepper1.begin(5, 1);  // 5 RPM and full step mode
  stepper2.begin(5, 1);

  digitalWrite(SLEEP_1, HIGH);
  digitalWrite(RESET_1, HIGH);

  digitalWrite(SLEEP_2, HIGH);
  digitalWrite(RESET_2, HIGH);

  // Set up limit switch as an input with internal pull-up resistor
  pinMode(LIMIT_SWITCH, INPUT);
}

void setSpeed()
{
  Serial.println("How often would you want the antenna to move (In terms of seconds)?");
  while (Serial.available() == 0) {}
  secondsBetweenMovement = Serial.parseFloat();
  Serial.print(secondsBetweenMovement);
  speedSet = 1;
}

void setAxis()
{
  Serial.println("What axis would you want to be the main point of rotating?\n\r 0 for X\n\r 1 for Y");
  while (Serial.available() == 0) {}
  int choice = Serial.parseInt();

  if (0 == choice)
  {
    movingAlongX = true;
    movingAlongY = false;
  }
  else if (1 == choice)
  {
    movingAlongX = false;
    movingAlongY = true;
  }
  else
  {
    movingAlongX = false;
    movingAlongY = false;
  }

  axisSet = 1;
}

void setAngle()
{
  Serial.println("What angle do you want the antenna to move?");
  while (Serial.available() == 0) {}
  angleBetweenMovement = Serial.parseFloat();
  angleSet = 1;
}

void read_serial() 
{
  if (Serial.available()) 
  {
    int command = Serial.parseInt();
  
    switch (command) 
    {
      case STOP:
        stopAllMotors();
        stopY = 0;
        break;
      case RESET:
        resetAllMotors();
        break;
      case SET:
        setInitalMotors();
        break;
      case TRACK:
        if (angleSet == 1 && speedSet == 1 && axisSet == 1)
          tracking = 1;
        else
          Serial.println("Not all parameters have been set...");
        break;
      case AXIS:
        setAxis();
        break;
      case SPEED:
        setSpeed();
        break;
      case ANGLE:
        setAngle();
        break;
      default:
        Serial.println("Invalid Command, please enter a valid command.");
        break;
    }
  }
}

void loop() 
{
    // Handle incoming serial commands
    read_serial();

    if (digitalRead(LIMIT_SWITCH) == HIGH) 
    {
      handleMotorSwitchCase();
    }

    // Perform tracking if enabled
    if (tracking == 1 && angleSet == 1 && speedSet == 1 && axisSet == 1) 
    {
      doTracking();
    }

    // Add a small delay to avoid flooding the serial output
    delay(100);
}
