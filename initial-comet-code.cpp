#include "Arduino.h"
#include "A4988.h"

#define MOTOR_STEPS 200

#define DIR_1 2
#define STEP_1 4
#define SLEEP_1 5
#define RESET_1 12
#define MS3_1 27
#define MS2_1 26
#define MS1_1 25
#define ENABLE_1 33

#define DIR_2 13
#define STEP_2 14
#define SLEEP_2 15
#define RESET_2 15
#define MS3_2 17
#define MS2_2 5
#define MS1_2 18
#define ENABLE_2 19

#define LIMIT_SWITCH 34  // Pin for the limit switch (must be interrupt-capable)

enum commands {
  STOP = 0x00,
  RESET = 0x01,
  SET = 0x02,
  TRACK = 0x03
};

A4988 stepper1(MOTOR_STEPS, DIR_1, STEP_1);
A4988 stepper2(MOTOR_STEPS, DIR_2, STEP_2);

// Variables to track the motor state
volatile bool stopMotors = false;
volatile bool limitSwitchPressed = false;  // To track if the switch is pressed or released
bool motorsRunning = true;  // Motors are running at the start

bool moveReverseX = false;
bool moveReverseY = false;

int stop = 1;
int tracking = 0;

int stepperXDegrees = 0;
int stepperYDegrees = 0;

// Interrupt service routine (ISR) for limit switch press and release
void IRAM_ATTR handleLimitSwitch() 
{
    if (digitalRead(LIMIT_SWITCH) == LOW) 
    {
      handleMotorSwitchCase();
    }
}

// Function to stop the motors
void stopAllMotors() 
{
    stepper1.stop();
    stepper2.stop();
    Serial.println("Motors stopped.");
}

void handleMotorSwitchCase() 
{
  stepper2.rotate(-10);  // Rotate stepper 2 back a small amount
  stepper2.stop();
  Serial.println("Y Motor hit the limit switch");
}

void resetAllMotors() 
{
  resetXMotor();
  resetYMotor();
  Serial.println("Both motors reset to initial positions.");
}

void doTracking() 
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

  if (false == moveReverseY) 
  {
      stepper2.rotate(10);
      stepperYDegrees += 10;
      Serial.print("stepperYDegrees: ");
      Serial.println(stepperYDegrees);  // Correct way to print float value
  } 
  else 
  {
      stepper2.rotate(-10);
      stepperYDegrees -= 10;
      Serial.print("stepperYDegrees: ");
      Serial.println(stepperYDegrees);  // Correct way to print float value
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

      Serial.println("What angle would you want to set for the Y Motor?");
      while (Serial.available() == 0) {}
      float y_angle = Serial.parseFloat();

      setMotorX(x_angle);
      setMotorY(y_angle);

      Serial.println("Satisfied?\n 0 for Yes\n 1 for No\n");
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
    stepper1.begin(5, 1);  // 0.25 RPM and full step mode
    stepper2.begin(5, 1);

    // Set up limit switch as an input with internal pull-up resistor
    pinMode(LIMIT_SWITCH, INPUT_PULLUP);

    // Attach the interrupt to the limit switch pin
    attachInterrupt(digitalPinToInterrupt(LIMIT_SWITCH), handleLimitSwitch, LOW);
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
        stop = 1;
        tracking = 0;
        break;
      case RESET:
        resetAllMotors();
        break;
      case SET:
        setInitalMotors();
        stop = 0;
        break;
      case TRACK:
        tracking = 1;
        stop = 0;
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

    // Perform tracking if enabled
    if (tracking == 1) 
    {
      doTracking();
    }

    // Add a small delay to avoid flooding the serial output
    delay(100);
}
